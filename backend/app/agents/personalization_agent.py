"""Personalization Agent: outreach copy from verified research only."""

from typing import Any

from app.agents.base import BaseAgent
from app.agents.results import PersonalizationResult
from app.prompts import personalization as prompt


class PersonalizationAgent(BaseAgent):
    name = "personalization"

    async def run(
        self,
        lead: dict[str, Any],
        research_summary: str = "",
        pain_points: list[str] | None = None,
    ) -> PersonalizationResult:
        pain_points = pain_points or []
        response = await self.chat_json(
            system=prompt.ROLE,
            user=prompt.build_user_prompt(lead, research_summary, pain_points),
            output_schema=prompt.OUTPUT_SCHEMA,
        )
        if response and isinstance(response.get("message"), str) and response["message"].strip():
            message = response["message"].strip()[:3000]
            default_subject = f"Quick question about {lead.get('company_name', '')}"
            subject = str(response.get("subject") or default_subject)[:300]
            used_facts = [str(f)[:200] for f in (response.get("used_facts") or [])][:10]
            omitted = [str(f)[:200] for f in (response.get("omitted_info") or [])][:10]
            return PersonalizationResult(
                subject=subject,
                message=message,
                used_facts=used_facts,
                omitted_info=omitted,
                used_llm=True,
            )
        return self._fallback_message(lead, pain_points)

    def _fallback_message(
        self, lead: dict[str, Any], pain_points: list[str]
    ) -> PersonalizationResult:
        """Offline fallback: only company name and industry, no invented facts."""
        company = str(lead.get("company_name") or "your company")
        industry = str(lead.get("industry") or "your industry")
        subject = f"Quick thought for {company}"
        message = (
            f"Hi,\n\nI came across {company} while researching {industry} businesses "
            "and wanted to reach out. We help teams in this space keep their outreach "
            "personal and their pipeline moving without adding manual work.\n\n"
            "Would you be open to a short conversation this week? If this isn't a "
            "priority right now, just let me know and I'll stop following up."
        )
        omitted: list[str] = []
        if not pain_points:
            omitted.append("pain_points: unknown, not referenced")
        if not lead.get("research_summary"):
            omitted.append("research details: unavailable, not referenced")
        if not lead.get("contact_name"):
            omitted.append("contact name: unknown, generic greeting used")
        return PersonalizationResult(
            subject=subject,
            message=message,
            used_facts=[f"company_name: {company}"],
            omitted_info=omitted,
            used_llm=False,
        )
