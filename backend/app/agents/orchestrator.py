"""Agent Orchestrator: coordinates agent execution and persists verified results.

Coordinates only — each agent remains an independently testable module and all
database access goes through repositories.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.discovery_agent import DiscoveryAgent
from app.agents.enrichment_agent import EnrichmentAgent
from app.agents.followup_agent import FollowupAgent, state_from_lead_status
from app.agents.personalization_agent import PersonalizationAgent
from app.agents.qualification_agent import QualificationAgent
from app.agents.research_agent import ResearchAgent
from app.core.errors import AppError
from app.core.logging import get_logger
from app.integrations.llm.embeddings import embed_lead_text
from app.models.agent_run import AgentRun
from app.models.enums import AgentRunStatus, AgentType, LeadStatus
from app.models.lead import Lead
from app.repositories.agent_repository import AgentRepository
from app.repositories.lead_repository import LeadRepository
from app.utils.helpers import compact_summary
from app.utils.normalization import normalize_domain, normalize_email
from app.utils.validators import can_transition

logger = get_logger(__name__)

MAX_LEADS_PER_RUN = 50


class Orchestrator:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.leads = LeadRepository(session)
        self.runs = AgentRepository(session)
        self.discovery = DiscoveryAgent()
        self.enrichment = EnrichmentAgent()
        self.research = ResearchAgent()
        self.qualification = QualificationAgent()
        self.personalization = PersonalizationAgent()
        self.followup = FollowupAgent()

    async def execute(self, run_id: str) -> AgentRun:
        run = await self.runs.get(run_id)
        if run is None:
            raise AppError("RUN_NOT_FOUND", "Agent run does not exist.", 404)

        await self.runs.update(
            run,
            {
                "status": AgentRunStatus.RUNNING.value,
                "started_at": datetime.now(UTC),
                "progress": 0,
            },
        )
        await self.session.commit()

        try:
            agent_type = run.agent_type
            if agent_type == AgentType.PIPELINE.value:
                output = await self._execute_pipeline(run)
            else:
                output = await self._execute_single(run, agent_type)
            await self.runs.update(
                run,
                {
                    "status": AgentRunStatus.COMPLETED.value,
                    "completed_at": datetime.now(UTC),
                    "progress": 100,
                    "output_summary": compact_summary(output),
                    "error": None,
                    "duration": self._duration(run),
                },
            )
            await self.session.commit()
            return run
        except Exception as exc:  # noqa: BLE001 - run must always record failure
            logger.exception("Agent run %s failed", run_id)
            await self.session.rollback()
            await self.runs.update(
                run,
                {
                    "status": AgentRunStatus.FAILED.value,
                    "completed_at": datetime.now(UTC),
                    "error": str(exc)[:1000],
                    "duration": self._duration(run),
                },
            )
            await self.session.commit()
            return run

    @staticmethod
    def _duration(run: AgentRun) -> float | None:
        if run.started_at is None or run.completed_at is None:
            return None
        return round((run.completed_at - run.started_at).total_seconds(), 3)

    async def _set_progress(self, run: AgentRun, progress: int) -> None:
        await self.runs.update(run, {"progress": max(0, min(progress, 100))})
        await self.session.commit()

    def _owner(self, run: AgentRun) -> UUID:
        return UUID(str(run.user_id))

    def _input(self, run: AgentRun) -> dict:
        return dict(run.input_summary or {})

    @staticmethod
    def _lead_ids(run: AgentRun) -> list[UUID]:
        raw = run.input_summary.get("lead_ids") or []
        ids: list[UUID] = []
        for item in raw:
            try:
                ids.append(UUID(str(item)))
            except ValueError:
                continue
        return ids

    @staticmethod
    def _icp(run: AgentRun) -> dict:
        icp = run.input_summary.get("icp") or {}
        return icp if isinstance(icp, dict) else {}

    async def _target_leads(self, run: AgentRun) -> list[Lead]:
        owner_id = self._owner(run)
        lead_ids = self._lead_ids(run)
        leads = await self.leads.get_many(lead_ids, owner_id)
        return leads[:MAX_LEADS_PER_RUN]

    async def _execute_pipeline(self, run: AgentRun) -> dict:
        owner_id = self._owner(run)
        icp = self._icp(run)
        output: dict = {}

        discovered_ids: list[str] = []
        if not self._lead_ids(run):
            discovery = await self.discovery.run(icp, limit=min(MAX_LEADS_PER_RUN, 20))
            await self._set_progress(run, 15)
            created, duplicates = await self._persist_discovered(
                owner_id, discovery.leads, run
            )
            discovered_ids = [str(lead.id) for lead in created]
            output["discovery"] = {
                "found": discovery.selected,
                "created": len(created),
                "duplicates_skipped": duplicates,
                "provider": discovery.provider,
                "used_llm": discovery.used_llm,
                "notes": discovery.notes,
            }
        else:
            output["discovery"] = {"skipped": True, "reason": "lead_ids provided"}

        if discovered_ids:
            leads = await self.leads.get_many([UUID(i) for i in discovered_ids], owner_id)
        else:
            leads = await self._target_leads(run)
        if not leads:
            output["note"] = "No leads to process."
            return output

        total_steps = len(leads) * 4
        step = 0

        for lead in leads:
            await self._enrich_lead(lead, icp)
            step += 1
            await self._set_progress(run, 15 + int(35 * step / total_steps))
        for lead in leads:
            await self._research_lead(lead, icp)
            step += 1
            await self._set_progress(run, 15 + int(45 * step / total_steps))
        for lead in leads:
            await self._qualify_lead(lead, icp)
            step += 1
            await self._set_progress(run, 15 + int(55 * step / total_steps))
        for lead in leads:
            await self._personalize_lead(lead)
            step += 1
            await self._set_progress(run, 15 + int(75 * step / total_steps))

        output["processed"] = len(leads)
        output["qualified"] = sum(
            1 for lead in leads if lead.status == LeadStatus.QUALIFIED.value
        )
        return output

    async def _execute_single(self, run: AgentRun, agent_type: str) -> dict:
        owner_id = self._owner(run)
        icp = self._icp(run)

        if agent_type == AgentType.DISCOVERY.value:
            discovery = await self.discovery.run(icp, limit=min(MAX_LEADS_PER_RUN, 20))
            created, duplicates = await self._persist_discovered(
                owner_id, discovery.leads, run
            )
            return {
                "found": discovery.selected,
                "created": len(created),
                "duplicates_skipped": duplicates,
                "provider": discovery.provider,
                "used_llm": discovery.used_llm,
            }

        leads = await self._target_leads(run)
        if not leads:
            raise AppError("NO_LEADS", "No accessible leads for this run.", 400)

        output: dict = {"processed": 0}
        for index, lead in enumerate(leads, start=1):
            if agent_type == AgentType.ENRICHMENT.value:
                await self._enrich_lead(lead, icp)
            elif agent_type == AgentType.RESEARCH.value:
                await self._research_lead(lead, icp)
            elif agent_type == AgentType.QUALIFICATION.value:
                await self._qualify_lead(lead, icp)
            elif agent_type == AgentType.PERSONALIZATION.value:
                await self._personalize_lead(lead)
            elif agent_type == AgentType.FOLLOWUP.value:
                await self._followup_lead(lead)
            else:
                raise AppError("UNKNOWN_AGENT", f"Unknown agent type '{agent_type}'.", 400)
            output["processed"] += 1
            await self._set_progress(run, int(100 * index / len(leads)))
        return output

    async def _persist_discovered(
        self,
        owner_id: UUID,
        candidates: list[dict],
        run: AgentRun,
    ) -> tuple[list[Lead], int]:
        created: list[Lead] = []
        duplicates = 0
        for candidate in candidates[:MAX_LEADS_PER_RUN]:
            domain = normalize_domain(candidate.get("website"))
            email = normalize_email(candidate.get("email"))
            duplicate = await self.leads.find_duplicate(
                owner_id, normalized_domain=domain, normalized_email=email
            )
            if duplicate is not None:
                duplicates += 1
                continue
            embedding = embed_lead_text(
                [
                    candidate.get("company_name"),
                    candidate.get("industry"),
                    candidate.get("description"),
                    candidate.get("location"),
                ]
            )
            lead = Lead(
                owner_id=owner_id,
                campaign_id=UUID(str(run.campaign_id)) if run.campaign_id else None,
                company_name=str(candidate.get("company_name") or "").strip() or "Unnamed",
                website=candidate.get("website"),
                industry=candidate.get("industry"),
                location=candidate.get("location"),
                company_size=candidate.get("company_size"),
                contact_name=candidate.get("contact_name"),
                contact_role=candidate.get("contact_role"),
                email=email,
                phone=candidate.get("phone"),
                linkedin_url=candidate.get("linkedin_url"),
                source=candidate.get("source"),
                source_url=candidate.get("source_url"),
                description=candidate.get("description"),
                normalized_domain=domain,
                normalized_email=email,
                status=LeadStatus.NEW.value,
                field_confidence={"source": str(candidate.get("source") or "unknown")},
                embedding=embedding,
            )
            created.append(await self.leads.add(lead))
        await self.session.commit()
        logger.info(
            "Run %s discovery created=%s duplicates=%s campaign=%s",
            run.run_id,
            len(created),
            duplicates,
            run.campaign_id,
        )
        return created, duplicates

    async def _enrich_lead(self, lead: Lead, icp: dict) -> None:
        if lead.status == LeadStatus.NEW.value:
            if can_transition(lead.status, LeadStatus.ENRICHING.value):
                lead.status = LeadStatus.ENRICHING.value
                await self.session.flush()
        lead_data = self._lead_dict(lead)
        context = f"ICP: {compact_summary(icp, 300)}"
        result = await self.enrichment.run(lead_data, context=context)
        updates: dict = {}
        for field, value in result.fields.items():
            if field in {"website_domain"} or not hasattr(lead, field):
                continue
            current = getattr(lead, field)
            if current in (None, "") and value not in (None, ""):
                updates[field] = value
        updates["field_confidence"] = result.field_confidence
        if updates.get("website") or updates.get("email"):
            updates["normalized_domain"] = normalize_domain(
                str(updates.get("website") or lead.website)
            )
            updates["normalized_email"] = normalize_email(
                str(updates.get("email") or lead.email)
            )
        updates["embedding"] = embed_lead_text(
            [
                str(updates.get("company_name") or lead.company_name),
                str(updates.get("industry") or lead.industry),
                str(updates.get("description") or lead.description),
                str(updates.get("location") or lead.location),
            ]
        )
        await self.leads.apply(lead, updates)
        await self.session.commit()

    async def _research_lead(self, lead: Lead, icp: dict) -> None:
        context = f"ICP: {compact_summary(icp, 300)}"
        result = await self.research.run(self._lead_dict(lead), context=context)
        await self.leads.apply(
            lead,
            {
                "research_summary": result.summary,
                "pain_points": result.pain_points,
            },
        )
        await self.session.commit()

    async def _qualify_lead(self, lead: Lead, icp: dict) -> None:
        research = {
            "pain_points": lead.pain_points or [],
            "buying_signals": [],
            "summary": lead.research_summary or "",
        }
        result = await self.qualification.run(self._lead_dict(lead), icp, research)
        updates = {
            "lead_score": result.score,
            "qualification": result.category,
            "qualification_reasons": result.reasons,
        }
        target_status = (
            LeadStatus.QUALIFIED.value
            if result.score >= 40
            else LeadStatus.UNQUALIFIED.value
        )
        if can_transition(lead.status, target_status):
            updates["status"] = target_status
        await self.leads.apply(lead, updates)
        await self.session.commit()

    async def _personalize_lead(self, lead: Lead) -> None:
        if lead.status == LeadStatus.DO_NOT_CONTACT.value:
            return
        result = await self.personalization.run(
            self._lead_dict(lead),
            research_summary=lead.research_summary or "",
            pain_points=list(lead.pain_points or []),
        )
        await self.leads.apply(lead, {"personalized_message": result.message})
        await self.session.commit()

    async def _followup_lead(self, lead: Lead) -> None:
        state = lead.followup_state or state_from_lead_status(lead.status)
        result = await self.followup.run(self._lead_dict(lead), state)
        await self.leads.apply(lead, {"followup_state": result.state})
        await self.session.commit()

    @staticmethod
    def _lead_dict(lead: Lead) -> dict:
        return {
            "company_name": lead.company_name,
            "website": lead.website,
            "industry": lead.industry,
            "location": lead.location,
            "company_size": lead.company_size,
            "contact_name": lead.contact_name,
            "contact_role": lead.contact_role,
            "email": lead.email,
            "phone": lead.phone,
            "linkedin_url": lead.linkedin_url,
            "source": lead.source,
            "description": lead.description,
            "status": lead.status,
            "lead_score": lead.lead_score,
            "qualification": lead.qualification,
            "research_summary": lead.research_summary,
            "pain_points": list(lead.pain_points or []),
        }
