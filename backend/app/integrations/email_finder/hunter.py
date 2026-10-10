"""Hunter.io email finder (HTTP API, no vendor SDK).

Docs: https://hunter.io/api-documentation
- `GET /email-finder` → one best email for (domain + first/last name).
- `GET /domain-search` → emails Hunter knows for a domain (used when the lead
  has no contact name).

Only emails Hunter actually returns are used; nothing is invented.
"""

from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.email_finder.base import (
    EmailFinderError,
    EmailFinderProvider,
    FoundEmail,
)

logger = get_logger(__name__)


class HunterEmailFinder(EmailFinderProvider):
    name = "hunter"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.hunter_api_key
        self._base_url = (base_url or settings.hunter_base_url).rstrip("/")
        self._timeout = timeout or settings.hunter_timeout_seconds

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    async def _get(self, path: str, params: dict[str, str]) -> dict[str, Any]:
        query = {**params, "api_key": self._api_key or ""}
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(f"{self._base_url}/{path}", params=query)
        except httpx.HTTPError as exc:
            raise EmailFinderError("Hunter request failed.") from exc

        if response.status_code >= 400:
            raise EmailFinderError(f"Hunter returned HTTP {response.status_code}.")

        data = response.json()
        return data if isinstance(data, dict) else {}

    @staticmethod
    def _verification_status(payload: dict[str, Any]) -> str | None:
        verification = payload.get("verification")
        if isinstance(verification, dict):
            status = verification.get("status")
            return str(status) if status else None
        return None

    @classmethod
    def _to_found(cls, email: str | None, score: Any, verified: bool) -> FoundEmail | None:
        if not email:
            return None
        numeric = score if isinstance(score, (int, float)) else None
        return FoundEmail(
            email=str(email),
            source=cls.name,
            score=int(numeric) if numeric is not None else None,
            confidence="verified" if verified else "unverified",
        )

    async def find_email(
        self,
        *,
        domain: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> FoundEmail | None:
        if not self.is_configured:
            raise EmailFinderError("Email finder is not configured (set HUNTER_API_KEY).")

        domain = (domain or "").strip().lower()
        if not domain:
            return None

        if first_name and last_name:
            data = await self._get(
                "email-finder",
                {"domain": domain, "first_name": first_name, "last_name": last_name},
            )
            payload = data.get("data")
            if not isinstance(payload, dict):
                return None
            verified = self._verification_status(payload) == "valid"
            return self._to_found(payload.get("email"), payload.get("score"), verified)

        data = await self._get("domain-search", {"domain": domain, "limit": "10"})
        payload = data.get("data")
        if not isinstance(payload, dict):
            return None
        emails = payload.get("emails")
        if not isinstance(emails, list):
            return None

        best: tuple[int, FoundEmail] | None = None
        for item in emails:
            if not isinstance(item, dict):
                continue
            found = self._to_found(
                item.get("value"),
                item.get("confidence"),
                self._verification_status(item) == "valid",
            )
            if found is None:
                continue
            score = found.score or 0
            if best is None or score > best[0]:
                best = (score, found)
        return best[1] if best else None
