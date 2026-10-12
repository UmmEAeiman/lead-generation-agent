"""Enrichment Agent: fill missing lead fields without fabricating data."""

from typing import Any

from app.agents.base import BaseAgent
from app.agents.results import EnrichmentResult
from app.integrations.contact_finder.base import ContactFinder, ContactFinderError
from app.integrations.contact_finder.factory import get_contact_finder
from app.integrations.email_finder.base import EmailFinderError, EmailFinderProvider
from app.integrations.email_finder.factory import get_email_finder
from app.integrations.llm.base import BaseLLMProvider
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

    def __init__(
        self,
        llm: BaseLLMProvider | None = None,
        email_finder: EmailFinderProvider | None = None,
        contact_finder: ContactFinder | None = None,
    ) -> None:
        super().__init__(llm)
        self.email_finder = email_finder or get_email_finder()
        self.contact_finder = contact_finder or get_contact_finder()

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
        if not fields.get("email"):
            await self._find_contact(fields, confidence)
        if not fields.get("email"):
            await self._find_email(fields, confidence)
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

    async def _find_contact(self, fields: dict[str, Any], confidence: dict[str, str]) -> None:
        """Discover a contact from the company's own site / search (free)."""
        if not self.contact_finder.is_configured:
            return
        domain = normalize_domain(str(fields.get("website") or ""))
        if not domain:
            return
        try:
            contacts = await self.contact_finder.find_contacts(
                domain=domain,
                company_name=str(fields.get("company_name") or "") or None,
                website=str(fields.get("website") or "") or None,
            )
        except ContactFinderError:
            return
        best = self._best_contact(contacts)
        if best is None:
            return
        normalized = normalize_email(best.email)
        if not normalized:
            return
        fields["email"] = normalized
        confidence["email"] = best.confidence
        if best.full_name and not fields.get("contact_name"):
            fields["contact_name"] = best.full_name
            confidence["contact_name"] = best.confidence
        if best.role and not fields.get("contact_role"):
            fields["contact_role"] = best.role
            confidence["contact_role"] = best.confidence

    _GENERIC_PREFIXES = (
        "info",
        "sales",
        "contact",
        "hello",
        "admin",
        "support",
        "office",
        "team",
        "enquiries",
        "inquiry",
        "mail",
        "welcome",
        "help",
        "billing",
    )

    @classmethod
    def _best_contact(cls, contacts: list[Any]) -> Any | None:
        if not contacts:
            return None

        def rank(contact: Any) -> tuple[bool, bool]:
            local = str(contact.email).split("@")[0].lower()
            generic = any(local.startswith(prefix) for prefix in cls._GENERIC_PREFIXES)
            return (not generic, contact.confidence == "verified")

        return max(contacts, key=rank)

    async def _find_email(self, fields: dict[str, Any], confidence: dict[str, str]) -> None:
        """Look up a contact email via the configured finder (never invent one)."""
        if not self.email_finder.is_configured:
            return
        domain = normalize_domain(str(fields.get("website") or ""))
        if not domain:
            return
        first_name, last_name = self._split_name(fields.get("contact_name"))
        try:
            found = await self.email_finder.find_email(
                domain=domain, first_name=first_name, last_name=last_name
            )
        except EmailFinderError:
            return
        if found is None:
            return
        normalized = normalize_email(found.email)
        if not normalized:
            return
        fields["email"] = normalized
        confidence["email"] = found.confidence

    @staticmethod
    def _split_name(name: Any) -> tuple[str | None, str | None]:
        parts = str(name or "").split()
        if not parts:
            return None, None
        if len(parts) == 1:
            return parts[0], None
        return parts[0], parts[-1]
