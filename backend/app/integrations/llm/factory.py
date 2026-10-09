"""LLM provider factory. The rest of the app only imports this module."""

from typing import Any

from app.core.config import settings
from app.integrations.llm.base import BaseLLMProvider, LLMUnavailableError
from app.integrations.llm.groq import GroqProvider


class UnconfiguredProvider(BaseLLMProvider):
    name = "none"

    @property
    def is_configured(self) -> bool:
        return False

    async def chat_json(
        self,
        *,
        system: str,
        user: str,
        task: str,
        output_schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        raise LLMUnavailableError("No LLM provider is configured (set GROQ_API_KEY).")


def get_llm_provider() -> BaseLLMProvider:
    if settings.llm_provider == "groq" and settings.groq_api_key:
        return GroqProvider()
    return UnconfiguredProvider()
