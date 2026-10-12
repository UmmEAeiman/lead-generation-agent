"""Contact-finder factory. The rest of the app only imports this module.

Contact discovery is intentionally free: the company's own website is scraped
and Serper search is used when a key is configured. No paid provider is
required (extend here to add one).
"""

from app.core.config import settings
from app.integrations.contact_finder.base import (
    CompositeContactFinder,
    ContactFinder,
    NullContactFinder,
)
from app.integrations.contact_finder.serper import SerperContactFinder
from app.integrations.contact_finder.website import WebsiteContactFinder


def get_contact_finder() -> ContactFinder:
    if not settings.contact_finder_enabled:
        return NullContactFinder()
    composite = CompositeContactFinder([WebsiteContactFinder(), SerperContactFinder()])
    if not composite.is_configured:
        return NullContactFinder()
    return composite
