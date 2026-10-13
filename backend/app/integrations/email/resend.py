"""Resend email provider (HTTP API, no vendor SDK).

Docs: https://resend.com/docs/api-reference/emails/send-email
"""

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.email.base import EmailProvider, EmailProviderError

logger = get_logger(__name__)


class ResendEmailProvider(EmailProvider):
    name = "resend"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        sender: str | None = None,
        sender_name: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.email_api_key
        self._base_url = (base_url or settings.email_base_url).rstrip("/")
        self._sender = sender or settings.email_from
        self._sender_name = sender_name if sender_name is not None else settings.email_from_name
        self._timeout = timeout or settings.email_timeout_seconds

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    def _from_header(self) -> str:
        if self._sender_name:
            return f"{self._sender_name} <{self._sender}>"
        return self._sender

    async def send_email(self, *, to: str, subject: str, body: str) -> str:
        if not self.is_configured:
            raise EmailProviderError("Email provider is not configured (set EMAIL_API_KEY).")

        payload = {
            "from": self._from_header(),
            "to": [to],
            "subject": subject,
            "text": body,
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/emails",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise EmailProviderError("Resend request failed.") from exc

        if response.status_code >= 400:
            detail = ""
            try:
                body = response.json()
                if isinstance(body, dict):
                    detail = str(body.get("message") or body.get("error") or "")
            except ValueError:
                detail = (response.text or "")[:200]
            message = f"Resend returned HTTP {response.status_code}."
            if detail:
                message = f"{message} {detail}"
            raise EmailProviderError(message)

        data = response.json()
        message_id = data.get("id") if isinstance(data, dict) else None
        return str(message_id or "")