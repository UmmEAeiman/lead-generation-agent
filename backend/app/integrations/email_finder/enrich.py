"""Enrich.so email finder (HTTP API, no vendor SDK).

Docs: https://doc.enrich.so
- `POST /api/v3/email-finder` finds one work email from a first name, last name
  and company domain. Both name parts are required — callers without a full name
  get None.

Only emails Enrich actually returns are used; nothing is invented.
"""

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.email_finder.base import (
    EmailFinderError,
    EmailFinderProvider,
    FoundEmail,
)

logger = get_logger(__name__)


class EnrichEmailFinder(EmailFinderProvider):
    name = "enrich"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.enrich_api_key
        self._base_url = (base_url or settings.enrich_base_url).rstrip("/")
        self._timeout = timeout or settings.enrich_timeout_seconds

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    async def find_email(
        self,
        *,
        domain: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> FoundEmail | None:
        if not self.is_configured:
            raise EmailFinderError("Email finder is not configured (set ENRICH_API_KEY).")

        domain = (domain or "").strip().lower()
        if not domain or not first_name or not last_name:
            return None

        payload = {"firstName": first_name, "lastName": last_name, "domain": domain}
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/api/v3/email-finder",
                    headers={
                        "x-api-key": self._api_key or "",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise EmailFinderError("Enrich request failed.") from exc

        if response.status_code == 202:
            logger.info("Enrich queued the lookup; skipping this run.")
            return None
        if response.status_code >= 400:
            raise EmailFinderError(f"Enrich returned HTTP {response.status_code}.")

        body = response.json()
        if not isinstance(body, dict):
            return None
        data = body.get("data") if isinstance(body.get("data"), dict) else {}
        email = data.get("email") or body.get("email")
        if not email:
            return None

        score = data.get("score", body.get("score"))
        numeric = score if isinstance(score, (int, float)) else None
        confidence = data.get("confidence") or body.get("confidence") or ""
        verified = bool(data.get("verified")) or str(confidence).lower() == "high"
        return FoundEmail(
            email=str(email),
            source=self.name,
            score=int(numeric) if numeric is not None else None,
            confidence="verified" if verified else "unverified",
        )
