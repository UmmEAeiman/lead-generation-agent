"""Search provider contract used by the Discovery Agent."""

from abc import ABC, abstractmethod
from typing import Any


class SearchProviderError(Exception):
    """The configured search provider failed or is unusable."""


class SearchProvider(ABC):
    name: str = "base"

    @property
    def is_configured(self) -> bool:
        return True

    @abstractmethod
    async def discover_leads(self, icp: dict[str, Any], limit: int = 20) -> list[dict[str, Any]]:
        """Return raw candidate lead dicts matching the ICP.

        Each result must include company_name and may include website,
        industry, location, company_size, contact_name, contact_role, email,
        phone, linkedin_url, source, source_url, description.
        """