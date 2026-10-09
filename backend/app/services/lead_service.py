"""Lead business logic. All persistence goes through LeadRepository."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import AppError, ConflictError, NotFoundError
from app.integrations.llm.embeddings import embed_lead_text
from app.models.lead import Lead
from app.repositories.lead_repository import LeadRepository
from app.schemas.lead import LeadCreate, LeadUpdate
from app.utils.normalization import normalize_domain, normalize_email, normalize_url
from app.utils.validators import can_transition


class LeadService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = LeadRepository(session)
        self.session = session

    async def create(
        self, owner_id: UUID, data: LeadCreate, campaign_id: UUID | None = None
    ) -> Lead:
        payload = data.model_dump()
        website = normalize_url(payload.get("website"))
        email = normalize_email(payload.get("email"))
        domain = normalize_domain(website)

        duplicate = await self.repo.find_duplicate(
            owner_id, normalized_domain=domain, normalized_email=email
        )
        if duplicate is not None:
            raise ConflictError(
                "DUPLICATE_LEAD",
                f"A lead already exists for this domain/email ({duplicate.company_name}).",
            )

        lead = Lead(
            owner_id=owner_id,
            campaign_id=campaign_id,
            company_name=payload["company_name"].strip(),
            website=website,
            industry=payload.get("industry"),
            location=payload.get("location"),
            company_size=payload.get("company_size"),
            contact_name=payload.get("contact_name"),
            contact_role=payload.get("contact_role"),
            email=email,
            phone=payload.get("phone"),
            linkedin_url=payload.get("linkedin_url"),
            source=payload.get("source"),
            source_url=payload.get("source_url"),
            description=payload.get("description"),
            normalized_domain=domain,
            normalized_email=email,
            embedding=embed_lead_text(
                [
                    payload["company_name"],
                    payload.get("industry"),
                    payload.get("description"),
                    payload.get("location"),
                ]
            ),
        )
        await self.repo.add(lead)
        await self.session.commit()
        return lead

    async def list(self, owner_id: UUID, **filters) -> tuple[list[Lead], int]:
        page = filters.pop("page", 1)
        requested = filters.pop("page_size", settings.page_size_default)
        page_size = min(requested, settings.page_size_max)
        return await self.repo.list(owner_id, page=page, page_size=page_size, **filters)

    async def get(self, owner_id: UUID, lead_id: UUID) -> Lead:
        lead = await self.repo.get_by_id(lead_id, owner_id)
        if lead is None:
            raise NotFoundError("LEAD_NOT_FOUND", "The requested lead does not exist.")
        return lead

    async def update(self, owner_id: UUID, lead_id: UUID, data: LeadUpdate) -> Lead:
        lead = await self.get(owner_id, lead_id)
        changes = data.model_dump(exclude_unset=True)

        new_status = changes.get("status")
        if new_status and not can_transition(lead.status, new_status):
            raise AppError(
                "INVALID_STATUS_TRANSITION",
                f"Cannot change status from {lead.status} to {new_status}.",
                422,
            )

        if "email" in changes:
            changes["email"] = normalize_email(changes.get("email"))
            changes["normalized_email"] = changes["email"]
        if "website" in changes:
            changes["website"] = normalize_url(changes.get("website"))
            changes["normalized_domain"] = normalize_domain(changes.get("website"))
        if changes.get("status") == "DO_NOT_CONTACT":
            changes["followup_state"] = "DO_NOT_CONTACT"

        for key, value in changes.items():
            if hasattr(lead, key):
                setattr(lead, key, value)
        if any(k in changes for k in ("company_name", "industry", "description", "location")):
            lead.embedding = embed_lead_text(
                [lead.company_name, lead.industry, lead.description, lead.location]
            )
        await self.session.commit()
        return lead

    async def delete(self, owner_id: UUID, lead_id: UUID) -> None:
        lead = await self.get(owner_id, lead_id)
        await self.session.delete(lead)
        await self.session.commit()

    async def similar(self, owner_id: UUID, query: str, limit: int = 10) -> list[Lead]:
        embedding = embed_lead_text([query])
        results = await self.repo.similar_leads(owner_id, embedding, limit=limit)
        return [lead for lead, _score in results]
