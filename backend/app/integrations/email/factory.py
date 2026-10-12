"""Email provider factory. The rest of the app only imports this module."""

from app.core.config import settings
from app.integrations.email.base import EmailProvider
from app.integrations.email.local import LocalEmailProvider
from app.integrations.email.resend import ResendEmailProvider
from app.integrations.email.smtp import SmtpEmailProvider

_local_provider: LocalEmailProvider | None = None


def get_email_provider() -> EmailProvider:
    """Return the configured provider, falling back to the local recorder.

    Set EMAIL_PROVIDER=smtp (+ SMTP_* vars) or EMAIL_PROVIDER=resend
    (+ EMAIL_API_KEY) to send real email.
    """
    if settings.email_provider == "smtp":
        smtp = SmtpEmailProvider()
        if smtp.is_configured:
            return smtp
    if settings.email_provider == "resend" and settings.email_api_key:
        return ResendEmailProvider()

    global _local_provider
    if _local_provider is None:
        _local_provider = LocalEmailProvider()
    return _local_provider