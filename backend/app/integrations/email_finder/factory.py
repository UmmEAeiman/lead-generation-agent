"""Email-finder factory. The rest of the app only imports this module."""

from app.core.config import settings
from app.integrations.email_finder.base import EmailFinderProvider, NullEmailFinder
from app.integrations.email_finder.enrich import EnrichEmailFinder
from app.integrations.email_finder.hunter import HunterEmailFinder


def get_email_finder() -> EmailFinderProvider:
    """Return the configured email finder, or a no-op when unconfigured.

    Set EMAIL_FINDER_PROVIDER=("hunter"|"enrich") plus the matching API key
    for live lookups.
    """
    if settings.email_finder_provider == "hunter" and settings.hunter_api_key:
        return HunterEmailFinder()
    if settings.email_finder_provider == "enrich" and settings.enrich_api_key:
        return EnrichEmailFinder()
    return NullEmailFinder()
