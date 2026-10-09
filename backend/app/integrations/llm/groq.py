"""Groq chat provider (OpenAI-compatible API)."""

import json
from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.llm.base import BaseLLMProvider, LLMProviderError, LLMUnavailableError

logger = get_logger(__name__)


class GroqProvider(BaseLLMProvider):
    name = "groq"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.groq_api_key
        self._base_url = (base_url or settings.groq_base_url).rstrip("/")
        self._model = model or settings.groq_model
        self._timeout = timeout or settings.llm_timeout_seconds
        self._client: httpx.AsyncClient | None = None

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    async def chat_json(
        self,
        *,
        system: str,
        user: str,
        task: str,
        output_schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.is_configured:
            raise LLMUnavailableError("GROQ_API_KEY is not configured.")

        schema_hint = (
            f"\nRespond ONLY with a JSON object matching this schema: "
            f"{json.dumps(output_schema)}" if output_schema else ""
        )
        payload = {
            "model": self._model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system + schema_hint},
                {"role": "user", "content": user},
            ],
        }
        try:
            response = await self._get_client().post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json=payload,
            )
            response.raise_for_status()
            body = response.json()
        except httpx.HTTPError as exc:
            logger.warning("Groq request failed for task=%s: %s", task, type(exc).__name__)
            raise LLMProviderError(f"Groq request failed for task {task}.") from exc

        try:
            content = body["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise LLMProviderError(f"Groq returned unusable JSON for task {task}.") from exc

        if not isinstance(parsed, dict):
            raise LLMProviderError(f"Groq returned a non-object JSON for task {task}.")
        return parsed

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
