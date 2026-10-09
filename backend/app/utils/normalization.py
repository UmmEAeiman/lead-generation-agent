"""Normalization helpers used for duplicate detection and storage consistency."""

import re
from urllib.parse import urlparse

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_domain(value: str | None) -> str | None:
    """Return a bare lowercase domain from a URL or domain string."""
    if not value:
        return None
    raw = value.strip().lower()
    if not raw:
        return None
    if "://" not in raw:
        raw = f"https://{raw}"
    parsed = urlparse(raw)
    host = parsed.netloc or parsed.path.split("/")[0]
    host = host.split("@")[-1].split(":")[0]
    host = host.removeprefix("www.").strip(".")
    return host or None


def normalize_email(value: str | None) -> str | None:
    if not value:
        return None
    email = value.strip().lower()
    if not _EMAIL_RE.match(email):
        return None
    return email


def normalize_url(value: str | None) -> str | None:
    if not value:
        return None
    raw = value.strip()
    if not raw:
        return None
    if "://" not in raw:
        raw = f"https://{raw}"
    return raw
