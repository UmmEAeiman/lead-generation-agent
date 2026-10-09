"""Email provider contract used by outreach. Never import a vendor SDK elsewhere."""

from abc import ABC, abstractmethod


class EmailProviderError(Exception):
    """The configured email provider failed or is unusable."""


class EmailProvider(ABC):
    name: str = "base"

    @property
    def is_configured(self) -> bool:
        return True

    @abstractmethod
    async def send_email(self, *, to: str, subject: str, body: str) -> str:
        """Send an email and return a provider message id."""