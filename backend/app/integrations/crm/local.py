"""Local CRM provider: keeps synced records in memory until a CRM is connected."""

from typing import Any

from app.integrations.crm.base import CRMProvider


class LocalCRMProvider(CRMProvider):
    name = "local"

    def __init__(self) -> None:
        self.records: dict[str, dict[str, Any]] = {}

    async def sync_lead(self, lead: dict[str, Any]) -> str:
        lead_id = str(lead.get("id") or f"crm-{len(self.records) + 1}")
        self.records[lead_id] = lead
        return lead_id
