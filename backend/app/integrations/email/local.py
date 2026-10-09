"""Local email provider: records messages instead of sending them.

Used until real SMTP/provider credentials are configured. Messages are logged
without secrets so outreach can be verified end to end.
"""

from app.core.logging import get_logger
from app.integrations.email.base import EmailProvider

logger = get_logger(__name__)


class LocalEmailProvider(EmailProvider):
    name = "local"

    def __init__(self) -> None:
        self.sent: list[dict[str, str]] = []

    async def send_email(self, *, to: str, subject: str, body: str) -> str:
        message_id = f"local-{len(self.sent) + 1}"
        self.sent.append({"to": to, "subject": subject, "body": body, "id": message_id})
        logger.info("Email recorded id=%s to=%s subject=%s", message_id, to, subject)
        return message_id
