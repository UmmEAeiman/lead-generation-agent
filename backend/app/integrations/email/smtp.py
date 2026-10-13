"""SMTP email provider (stdlib only) for free providers.

Works with any SMTP relay — Gmail (App Password), Brevo, SMTP2GO, Zoho, etc.
Configure with SMTP_HOST / SMTP_PORT / SMTP_USERNAME / SMTP_PASSWORD.
"""

import asyncio
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.email.base import EmailProvider, EmailProviderError

logger = get_logger(__name__)


class SmtpEmailProvider(EmailProvider):
    name = "smtp"

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        sender: str | None = None,
        sender_name: str | None = None,
        use_tls: bool | None = None,
        use_ssl: bool | None = None,
        timeout: float | None = None,
    ) -> None:
        self._host = host if host is not None else settings.smtp_host
        self._port = port or settings.smtp_port
        self._username = username if username is not None else settings.smtp_username
        self._password = password if password is not None else settings.smtp_password
        self._sender = sender or settings.email_from
        self._sender_name = (
            sender_name if sender_name is not None else settings.email_from_name
        )
        self._use_tls = settings.smtp_use_tls if use_tls is None else use_tls
        self._use_ssl = settings.smtp_use_ssl if use_ssl is None else use_ssl
        self._timeout = timeout or settings.email_timeout_seconds

    @property
    def is_configured(self) -> bool:
        return bool(self._host and self._sender)

    def _from_header(self) -> str:
        if self._sender_name:
            return f"{self._sender_name} <{self._sender}>"
        return self._sender

    def _send_sync(self, to: str, subject: str, body: str) -> str:
        message = EmailMessage()
        message["From"] = self._from_header()
        message["To"] = to
        message["Subject"] = subject
        message_id = make_msgid()
        message["Message-ID"] = message_id
        message.set_content(body)

        if self._use_ssl:
            smtp: smtplib.SMTP = smtplib.SMTP_SSL(
                self._host, self._port, timeout=self._timeout
            )
        else:
            smtp = smtplib.SMTP(self._host, self._port, timeout=self._timeout)

        try:
            if not self._use_ssl:
                smtp.ehlo()
                if self._use_tls:
                    smtp.starttls()
                    smtp.ehlo()
            if self._username:
                smtp.login(self._username, self._password or "")
            smtp.send_message(message)
        finally:
            try:
                smtp.quit()
            except smtplib.SMTPException:
                smtp.close()

        return message_id

    async def send_email(self, *, to: str, subject: str, body: str) -> str:
        if not self.is_configured:
            raise EmailProviderError(
                "SMTP provider is not configured (set SMTP_HOST and EMAIL_FROM)."
            )
        try:
            return await asyncio.to_thread(self._send_sync, to, subject, body)
        except (smtplib.SMTPException, OSError) as exc:
            logger.warning("SMTP send failed: %s", type(exc).__name__)
            raw = getattr(exc, "smtp_error", None)
            if isinstance(raw, (bytes, bytearray)):
                detail = raw.decode("utf-8", "replace").strip()
            else:
                detail = str(raw or "").strip()
            message = f"SMTP send failed ({type(exc).__name__})."
            if detail:
                message = f"{message} {detail}"[:400]
            raise EmailProviderError(message) from exc
