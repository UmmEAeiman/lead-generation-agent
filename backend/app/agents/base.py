"""Shared agent base: LLM access with graceful fallback when unconfigured."""

from typing import Any

from app.core.logging import get_logger
from app.integrations.llm.base import BaseLLMProvider, LLMError
from app.integrations.llm.factory import get_llm_provider

logger = get_logger(__name__)


class BaseAgent:
    name: str = "base"

    def __init__(self, llm: BaseLLMProvider | None = None) -> None:
        self.llm = llm or get_llm_provider()

    @property
    def used_llm(self) -> bool:
        return self.llm.is_configured

    async def chat_json(
        self,
        *,
        system: str,
        user: str,
        output_schema: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Return the provider's JSON, or None so the agent can fall back."""
        if not self.llm.is_configured:
            return None
        try:
            return await self.llm.chat_json(
                system=system,
                user=user,
                task=self.name,
                output_schema=output_schema,
            )
        except LLMError as exc:
            logger.info("Agent %s falling back to deterministic output: %s", self.name, exc)
            return None
