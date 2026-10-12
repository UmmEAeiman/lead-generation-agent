"""Website contact finder: reads a company's own public pages for contacts.

Only public GET requests are made (the homepage plus common contact/about/team
paths). Emails and names are taken verbatim from the returned HTML — nothing is
invented, and only emails on the target domain are kept.
"""

import asyncio
import html
import re
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.integrations.contact_finder.base import ContactFinder, FoundContact
from app.utils.normalization import normalize_domain

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_ANCHOR_RE = re.compile(
    r"""<a\b[^>]*href=["']mailto:([^"'?>]+)["'][^>]*>(.*?)</a>""",
    re.IGNORECASE | re.DOTALL,
)
_TAG_RE = re.compile(r"<[^>]+>")
_NAME_RE = re.compile(r"^[A-Z][A-Za-z'.\-]+(?:\s+[A-Z][A-Za-z'.\-]+){1,2}$")

_ROLE_WORDS = (
    "co-founder",
    "founder",
    "ceo",
    "cto",
    "cmo",
    "coo",
    "owner",
    "director",
    "manager",
    "head of",
    "president",
    "partner",
    "sales",
    "marketing",
    "business development",
    "account executive",
    "growth",
    "consultant",
    "specialist",
)

_PATH_CANDIDATES = (
    "",
    "/contact",
    "/contact-us",
    "/contactus",
    "/about",
    "/about-us",
    "/team",
    "/contact.html",
)

_MAX_CONCURRENT_PAGES = 6


def _clean_text(raw: str) -> str:
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _base_url(website: str | None, domain: str) -> str:
    raw = str(website or "").strip() or f"https://{domain}"
    if "://" not in raw:
        raw = f"https://{raw}"
    parsed = urlparse(raw)
    scheme = parsed.scheme or "https"
    host = parsed.netloc or domain
    return f"{scheme}://{host}"


def _is_target_domain(email: str, domain: str) -> bool:
    if "@" not in email:
        return False
    host = email.split("@")[-1].lower().strip(".")
    return host == domain or host.endswith("." + domain)


def _first_email(value: str) -> str | None:
    match = _EMAIL_RE.search(value or "")
    return match.group(0).strip(".").lower() if match else None


def _name_and_role(anchor_text: str, context: str) -> tuple[str | None, str | None]:
    haystack = f"{anchor_text} {context}".lower()
    role = next((word for word in _ROLE_WORDS if word in haystack), None)

    candidate = anchor_text.strip(" -·|,.")
    name = None
    if candidate and _NAME_RE.match(candidate):
        lowered = candidate.lower()
        if not any(word in lowered for word in _ROLE_WORDS):
            name = candidate
    return name, role


def _extract_contacts(raw_html: str, domain: str, page_url: str) -> list[FoundContact]:
    results: list[FoundContact] = []
    seen: set[str] = set()

    for value, anchor_html in _ANCHOR_RE.findall(raw_html):
        email = _first_email(value)
        if not email or not _is_target_domain(email, domain) or email in seen:
            continue
        name, role = _name_and_role(_clean_text(anchor_html), "")
        results.append(
            FoundContact(
                email=email,
                full_name=name,
                role=role,
                source="website",
                source_url=page_url,
                confidence="verified",
            )
        )
        seen.add(email)

    text = _clean_text(raw_html)
    for match in _EMAIL_RE.finditer(text):
        email = match.group(0).strip(".").lower()
        if not _is_target_domain(email, domain) or email in seen:
            continue
        context = text[max(0, match.start() - 120) : match.start() + 120]
        name, role = _name_and_role("", context)
        results.append(
            FoundContact(
                email=email,
                full_name=name,
                role=role,
                source="website",
                source_url=page_url,
                confidence="unverified",
            )
        )
        seen.add(email)

    return results


class WebsiteContactFinder(ContactFinder):
    name = "website"

    def __init__(
        self,
        timeout: float | None = None,
        max_pages: int | None = None,
        user_agent: str | None = None,
    ) -> None:
        self._timeout = timeout or settings.contact_finder_timeout_seconds
        self._max_pages = max_pages or settings.contact_finder_max_pages
        self._user_agent = user_agent or settings.contact_finder_user_agent

    @property
    def is_configured(self) -> bool:
        return True

    async def find_contacts(
        self,
        *,
        domain: str,
        company_name: str | None = None,
        website: str | None = None,
        limit: int = 5,
    ) -> list[FoundContact]:
        normalized = normalize_domain(domain)
        if not normalized:
            return []

        base = _base_url(website, normalized)
        paths = _PATH_CANDIDATES[: self._max_pages]
        headers = {
            "User-Agent": self._user_agent,
            "Accept": "text/html,application/xhtml+xml",
        }

        async with httpx.AsyncClient(
            timeout=self._timeout, follow_redirects=True, headers=headers
        ) as client:
            semaphore = asyncio.Semaphore(_MAX_CONCURRENT_PAGES)

            async def fetch(path: str) -> tuple[str, str] | None:
                url = f"{base}{path}"
                try:
                    async with semaphore:
                        response = await client.get(url)
                except httpx.HTTPError:
                    return None
                if response.status_code >= 400:
                    return None
                return url, response.text

            fetched = await asyncio.gather(*(fetch(path) for path in paths))

        results: list[FoundContact] = []
        seen: set[str] = set()
        for page in fetched:
            if page is None:
                continue
            url, text = page
            for contact in _extract_contacts(text, normalized, url):
                key = contact.email.lower()
                if key in seen:
                    continue
                seen.add(key)
                results.append(contact)
            if len(results) >= limit:
                break

        return results[:limit]
