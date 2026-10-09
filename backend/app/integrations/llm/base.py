"""Vendor-agnostic LLM provider contract."""

from abc import ABC, abstractmethod
from typing import Any


class LLMError(Exception):
    """Base LLM integration error."""


class LLMUnavailableError(LLMError):
    """No LLM provider is configured for this environment."""


class LLMProviderError(LLMError):
    """The configured provider failed or returned an unusable response."""


class BaseLLMProvider(ABC):
    name: str = "base"

    @property
    @abstractmethod
    def is_configured(self) -> bool: ...

    @abstractmethod
    async def chat_json(
        self,
        *,
        system: str,
        user: str,
        task: str,
        output_schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return a JSON object for the given prompt.

        Must raise LLMUnavailableError when no provider is configured and
        LLMProviderError when the provider fails or returns invalid JSON.
        """

    async def aclose(self) -> None:  # pragma: no cover - trivial default
        return None
