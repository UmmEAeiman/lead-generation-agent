"""Email-finder provider contract used by the Enrichment Agent.

An email finder proposes a contact email for a company domain. Providers must
return only emails they actually found — the agent never fabricates contacts.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class EmailFinderError(Exception):
    """The configured email-finder provider failed or is unusable."""


class FoundEmail(BaseModel):
    """A single email proposed by a finder provider."""

    email: str
    source: str
    score: int | None = None
    confidence: str = "unverified"


class EmailFinderProvider(ABC):
    name: str = "base"

    @property
    def is_configured(self) -> bool:
        return True

    @abstractmethod
    async def find_email(
        self,
        *,
        domain: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> FoundEmail | None:
        """Return the best email found for the domain, or None if none found."""


class NullEmailFinder(EmailFinderProvider):
    """Used when no finder is configured: always returns None, never invents."""

    name = "none"

    @property
    def is_configured(self) -> bool:
        return False

    async def find_email(
        self,
        *,
        domain: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> FoundEmail | None:
        return None
