"""CRM provider contract for syncing leads into a pipeline."""

from abc import ABC, abstractmethod
from typing import Any


class CRMProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def sync_lead(self, lead: dict[str, Any]) -> str:
        """Upsert a lead in the CRM and return the external record id."""
