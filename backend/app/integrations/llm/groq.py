"""Groq chat provider (OpenAI-compatible API)."""

import asyncio
import json
import random
import time
from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.llm.base import BaseLLMProvider, LLMProviderError, LLMUnavailableError

logger = get_logger(__name__)

# Groq's free tier is rate limited (HTTP 429). Pace requests globally and retry
# transient failures with backoff so agents rarely fall back to generic output.
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}
_MAX_ATTEMPTS = 5
_MIN_REQUEST_INTERVAL = 2.0
_MAX_BACKOFF = 15.0

_pace_lock = asyncio.Lock()
_last_request_at = 0.0


async def _throttle() -> None:
    """Serialize request starts and enforce a global minimum spacing."""
    global _last_request_at
    async with _pace_lock:
        wait = _MIN_REQUEST_INTERVAL - (time.monotonic() - _last_request_at)
        if wait > 0:
            await asyncio.sleep(wait)
        _last_request_at = time.monotonic()


def _retry_delay(response: httpx.Response | None, attempt: int) -> float:
    if response is not None:
        header = response.headers.get("retry-after")
        if header:
            try:
                return min(float(header), _MAX_BACKOFF)
            except ValueError:
                pass
    return min(0.8 * (2**attempt), _MAX_BACKOFF) + random.uniform(0, 0.4)


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
            body = await self._post_with_retry(payload, task)
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

    async def _post_with_retry(self, payload: dict[str, Any], task: str) -> dict[str, Any]:
        last_response: httpx.Response | None = None
        for attempt in range(_MAX_ATTEMPTS):
            await _throttle()
            response = await self._get_client().post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json=payload,
            )
            if response.status_code not in _RETRYABLE_STATUS:
                response.raise_for_status()
                return response.json()

            last_response = response
            if attempt < _MAX_ATTEMPTS - 1:
                delay = _retry_delay(response, attempt)
                logger.info(
                    "Groq %s for task=%s; retrying in %.1fs (%s/%s)",
                    response.status_code,
                    task,
                    delay,
                    attempt + 1,
                    _MAX_ATTEMPTS,
                )
                await asyncio.sleep(delay)

        last_response.raise_for_status()  # type: ignore[union-attr]
        raise LLMProviderError(f"Groq request failed for task {task}.")

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
