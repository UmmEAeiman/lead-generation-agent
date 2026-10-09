"""Discovery Agent: find candidate leads for an ICP."""

from typing import Any

from app.agents.base import BaseAgent
from app.agents.results import DiscoveryResult
from app.integrations.search.base import SearchProvider
from app.integrations.search.factory import get_search_provider
from app.prompts import discovery as prompt

_CLEAN_KEYS = (
    "company_name",
    "website",
    "industry",
    "location",
    "company_size",
    "contact_name",
    "contact_role",
    "email",
    "phone",
    "linkedin_url",
    "source",
    "source_url",
    "description",
)


class DiscoveryAgent(BaseAgent):
    name = "discovery"

    def __init__(
        self,
        llm: Any = None,
        search: SearchProvider | None = None,
    ) -> None:
        super().__init__(llm)
        self.search = search or get_search_provider()

    async def run(self, icp: dict[str, Any], limit: int = 20) -> DiscoveryResult:
        candidates = await self.search.discover_leads(icp, limit=limit)
        if not candidates:
            return DiscoveryResult(
                leads=[], provider=self.search.name, notes="No candidates returned."
            )

        selected_indices = list(range(len(candidates)))
        notes = "All candidates kept (no LLM filter configured)."
        used_llm = False

        response = await self.chat_json(
            system=prompt.ROLE,
            user=prompt.build_user_prompt(icp, candidates),
            output_schema=prompt.OUTPUT_SCHEMA,
        )
        if response is not None:
            raw_indices = response.get("selected_indices")
            if isinstance(raw_indices, list):
                cleaned = [
                    i for i in raw_indices if isinstance(i, int) and 0 <= i < len(candidates)
                ]
                if cleaned:
                    selected_indices = cleaned
                    notes = str(response.get("notes") or "Filtered by LLM.")
                    used_llm = True

        leads = []
        for index in selected_indices:
            candidate = candidates[index]
            clean = {key: candidate.get(key) for key in _CLEAN_KEYS}
            if clean.get("company_name"):
                leads.append(clean)

        return DiscoveryResult(
            leads=leads,
            provider=self.search.name,
            selected=len(leads),
            notes=notes,
            used_llm=used_llm,
        )
