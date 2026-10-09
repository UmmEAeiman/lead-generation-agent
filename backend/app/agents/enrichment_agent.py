"""Enrichment Agent: fill missing lead fields without fabricating data."""

from typing import Any

from app.agents.base import BaseAgent
from app.agents.results import EnrichmentResult
from app.models.enums import DataConfidence
from app.prompts import enrichment as prompt
from app.utils.normalization import normalize_domain, normalize_email, normalize_url

_ENRICHABLE_FIELDS = (
    "company_name",
    "website",
    "industry",
    "location",
    "company_size",
    "contact_name",
    "contact_role",
    "email",
    "description",
)


class EnrichmentAgent(BaseAgent):
    name = "enrichment"

    async def run(self, lead: dict[str, Any], context: str = "") -> EnrichmentResult:
        fields = dict(lead)
        confidence: dict[str, str] = {}
        for field in _ENRICHABLE_FIELDS:
            value = fields.get(field)
            if value in (None, ""):
                confidence[field] = DataConfidence.UNKNOWN.value
            else:
                confidence[field] = DataConfidence.UNVERIFIED.value

        # Local, rule-based enrichment that cannot invent data.
        if fields.get("website"):
            fields["website"] = normalize_url(str(fields["website"]))
            domain = normalize_domain(str(fields["website"]))
            if domain:
                fields["website_domain"] = domain
                confidence["website"] = DataConfidence.VERIFIED.value
        if fields.get("email"):
            normalized = normalize_email(str(fields["email"]))
            if normalized:
                fields["email"] = normalized
                confidence["email"] = DataConfidence.VERIFIED.value
        if not fields.get("industry") and context:
            confidence.setdefault("industry", DataConfidence.UNKNOWN.value)

        response = await self.chat_json(
            system=prompt.ROLE,
            user=prompt.build_user_prompt(lead, context),
            output_schema=prompt.OUTPUT_SCHEMA,
        )
        used_llm = False
        if response and isinstance(response.get("field_confidence"), dict):
            for field in _ENRICHABLE_FIELDS:
                new_conf = str(response.get("field_confidence", {}).get(field, "")).lower()
                if new_conf not in {
                    DataConfidence.VERIFIED.value,
                    DataConfidence.UNVERIFIED.value,
                    DataConfidence.UNKNOWN.value,
                }:
                    continue
                new_value = response.get(field)
                if new_conf == DataConfidence.UNKNOWN.value:
                    continue
                if new_value in (None, ""):
                    continue
                # Never let the LLM overwrite verified local data or invent contacts.
                if field in {"email", "contact_name", "contact_role"} and not lead.get(field):
                    continue
                if confidence.get(field) == DataConfidence.VERIFIED.value:
                    continue
                fields[field] = new_value
                confidence[field] = new_conf
            used_llm = True

        return EnrichmentResult(fields=fields, field_confidence=confidence, used_llm=used_llm)
