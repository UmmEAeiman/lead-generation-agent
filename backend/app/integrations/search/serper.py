"""Serper.dev search provider (Google search + Places via HTTP, no vendor SDK).

Docs: https://serper.dev/playground
- `POST /places` returns local businesses (title, address, phoneNumber, website,
  category) which map cleanly to leads when the ICP has a location.
- `POST /search` returns organic Google results (title, link, snippet).
"""

from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.search.base import SearchProvider, SearchProviderError

logger = get_logger(__name__)

_MAX_REQUESTED = 100


class SerperSearchProvider(SearchProvider):
    name = "serper"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        gl: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.search_api_key
        self._base_url = (base_url or settings.search_base_url).rstrip("/")
        self._gl = gl or settings.search_gl
        self._timeout = timeout or settings.search_timeout_seconds

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    @staticmethod
    def _keywords(icp: dict[str, Any]) -> list[str]:
        return [str(k).strip() for k in icp.get("keywords") or [] if str(k).strip()]

    def _build_query(self, icp: dict[str, Any]) -> str:
        industry = str(icp.get("industry") or "").strip()
        location = str(icp.get("location") or "").strip()
        subject = " ".join(filter(None, [industry, *self._keywords(icp)])) or "companies"
        if location:
            return f"{subject} in {location}"
        return subject

    def _endpoint(self, icp: dict[str, Any]) -> str:
        return "places" if str(icp.get("location") or "").strip() else "search"

    def _map_place(self, item: dict[str, Any], icp: dict[str, Any]) -> dict[str, Any] | None:
        company = item.get("title") or item.get("name")
        if not company:
            return None
        website = item.get("website")
        rating = item.get("rating")
        rating_count = item.get("ratingCount")
        description_parts = [str(item.get("category") or icp.get("industry") or "").strip()]
        if rating is not None:
            suffix = f" ({rating_count})" if rating_count else ""
            description_parts.append(f"rating {rating}{suffix}")
        description = " · ".join(p for p in description_parts if p) or None
        return {
            "company_name": str(company),
            "website": website,
            "industry": item.get("category") or icp.get("industry"),
            "location": item.get("address") or icp.get("location"),
            "company_size": None,
            "contact_name": None,
            "contact_role": None,
            "email": None,
            "phone": item.get("phoneNumber"),
            "linkedin_url": None,
            "source": self.name,
            "source_url": website or item.get("cid"),
            "description": description,
        }

    def _map_organic(self, item: dict[str, Any], icp: dict[str, Any]) -> dict[str, Any] | None:
        company = item.get("title")
        if not company:
            return None
        link = item.get("link")
        return {
            "company_name": str(company),
            "website": link,
            "industry": icp.get("industry"),
            "location": icp.get("location"),
            "company_size": None,
            "contact_name": None,
            "contact_role": None,
            "email": None,
            "phone": None,
            "linkedin_url": None,
            "source": self.name,
            "source_url": link,
            "description": item.get("snippet"),
        }

    async def discover_leads(self, icp: dict[str, Any], limit: int = 20) -> list[dict[str, Any]]:
        if not self.is_configured:
            raise SearchProviderError("Search provider is not configured (set SEARCH_API_KEY).")

        endpoint = self._endpoint(icp)
        payload: dict[str, Any] = {"q": self._build_query(icp), "gl": self._gl, "hl": "en"}
        if endpoint == "search":
            payload["num"] = min(max(limit, 1), _MAX_REQUESTED)

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/{endpoint}",
                    headers={"X-API-KEY": self._api_key or "", "Content-Type": "application/json"},
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise SearchProviderError("Serper request failed.") from exc

        if response.status_code >= 400:
            raise SearchProviderError(f"Serper returned HTTP {response.status_code}.")

        data = response.json()
        rows = data.get("places") if endpoint == "places" else data.get("organic")
        if not isinstance(rows, list):
            return []

        mapper = self._map_place if endpoint == "places" else self._map_organic
        results: list[dict[str, Any]] = []
        for item in rows:
            if isinstance(item, dict):
                mapped = mapper(item, icp)
                if mapped is not None:
                    results.append(mapped)
        return results[: max(limit, 1)]