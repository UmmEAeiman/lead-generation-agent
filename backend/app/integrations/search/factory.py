"""Search provider factory. The rest of the app only imports this module."""

from app.core.config import settings
from app.integrations.search.base import SearchProvider
from app.integrations.search.mock import MockSearchProvider
from app.integrations.search.serper import SerperSearchProvider


def get_search_provider() -> SearchProvider:
    """Return the configured provider, falling back to the offline sample.

    Set SEARCH_PROVIDER=serper and SEARCH_API_KEY for live discovery.
    """
    if settings.search_provider == "serper" and settings.search_api_key:
        return SerperSearchProvider()
    return MockSearchProvider()