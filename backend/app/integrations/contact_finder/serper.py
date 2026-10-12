"""Serper contact finder: finds published emails via Google search snippets.

Uses the Serper `/search` endpoint with targeted email queries and reads emails
from the returned titles/snippets. Only emails on the target domain are kept;
nothing is invented.
"""

import re

import httpx

from app.core.config import settings
from app.integrations.contact_finder.base import (
    ContactFinder,
    ContactFinderError,
    FoundContact,
)
from app.utils.normalization import normalize_domain

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


class SerperContactFinder(ContactFinder):
    name = "serper-contact"

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
    def _queries(domain: str, company_name: str | None) -> list[str]:
        # Free Serper accounts reject "@domain" style queries, so use plain
        # keyword queries that still surface published emails in snippets.
        queries = [f"{domain} email"]
        if company_name:
            queries.append(f"{company_name} email")
        else:
            queries.append(f"{domain} contact email")
        return queries

    @staticmethod
    def _is_target(email: str, domain: str) -> bool:
        host = email.split("@")[-1].lower().strip(".")
        return host == domain or host.endswith("." + domain)

    async def _search(self, client: httpx.AsyncClient, query: str) -> list[dict]:
        try:
            response = await client.post(
                f"{self._base_url}/search",
                headers={
                    "X-API-KEY": self._api_key or "",
                    "Content-Type": "application/json",
                },
                json={"q": query, "gl": self._gl, "hl": "en", "num": 10},
            )
        except httpx.HTTPError as exc:
            raise ContactFinderError("Serper request failed.") from exc
        if response.status_code >= 400:
            raise ContactFinderError(f"Serper returned HTTP {response.status_code}.")
        data = response.json()
        rows = data.get("organic")
        return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []

    async def find_contacts(
        self,
        *,
        domain: str,
        company_name: str | None = None,
        website: str | None = None,
        limit: int = 5,
    ) -> list[FoundContact]:
        if not self.is_configured:
            raise ContactFinderError(
                "Serper contact finder is not configured (set SEARCH_API_KEY)."
            )
        normalized = normalize_domain(domain)
        if not normalized:
            return []

        results: list[FoundContact] = []
        seen: set[str] = set()
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            for query in self._queries(normalized, company_name):
                for row in await self._search(client, query):
                    blob = " ".join(
                        str(row.get(key) or "") for key in ("title", "snippet", "link")
                    )
                    for match in _EMAIL_RE.finditer(blob):
                        email = match.group(0).strip(".").lower()
                        if email in seen or not self._is_target(email, normalized):
                            continue
                        seen.add(email)
                        results.append(
                            FoundContact(
                                email=email,
                                source="serper",
                                source_url=str(row.get("link") or "") or None,
                                confidence="unverified",
                            )
                        )
                        if len(results) >= limit:
                            return results
        return results
