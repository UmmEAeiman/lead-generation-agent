"""Contact-finder provider contract used by the Enrichment Agent.

A contact finder proposes business contacts (name, role, email) for a company
domain by reading the company's own public pages or search results. Providers
must return only contacts they actually found — nothing is ever invented.
"""

import asyncio
from abc import ABC, abstractmethod

from pydantic import BaseModel


class ContactFinderError(Exception):
    """The configured contact-finder provider failed or is unusable."""


class FoundContact(BaseModel):
    """A single contact proposed by a finder provider."""

    email: str
    full_name: str | None = None
    role: str | None = None
    source: str
    source_url: str | None = None
    confidence: str = "unverified"


class ContactFinder(ABC):
    name: str = "base"

    @property
    def is_configured(self) -> bool:
        return True

    @abstractmethod
    async def find_contacts(
        self,
        *,
        domain: str,
        company_name: str | None = None,
        website: str | None = None,
        limit: int = 5,
    ) -> list[FoundContact]:
        """Return contacts found for the domain (may be empty)."""


class NullContactFinder(ContactFinder):
    name = "none"

    @property
    def is_configured(self) -> bool:
        return False

    async def find_contacts(
        self,
        *,
        domain: str,
        company_name: str | None = None,
        website: str | None = None,
        limit: int = 5,
    ) -> list[FoundContact]:
        return []


class CompositeContactFinder(ContactFinder):
    """Runs several finders in order and merges their results (dedup by email)."""

    name = "composite"

    def __init__(self, finders: list[ContactFinder]) -> None:
        self._finders = [finder for finder in finders if finder.is_configured]

    @property
    def is_configured(self) -> bool:
        return bool(self._finders)

    async def find_contacts(
        self,
        *,
        domain: str,
        company_name: str | None = None,
        website: str | None = None,
        limit: int = 5,
    ) -> list[FoundContact]:
        async def run(finder: ContactFinder) -> list[FoundContact]:
            try:
                return await finder.find_contacts(
                    domain=domain,
                    company_name=company_name,
                    website=website,
                    limit=limit,
                )
            except ContactFinderError:
                return []

        groups = await asyncio.gather(*(run(finder) for finder in self._finders))

        results: list[FoundContact] = []
        seen: set[str] = set()
        for found in groups:
            for contact in found:
                key = contact.email.strip().lower()
                if not key or key in seen:
                    continue
                seen.add(key)
                results.append(contact)
                if len(results) >= limit:
                    return results
        return results
