"""Deterministic offline discovery source for development and tests.

Results are clearly marked with source="offline-sample" so nothing here can be
mistaken for verified production data.
"""

import hashlib
from typing import Any

from app.integrations.search.base import SearchProvider

_SUFFIXES = ["Group", "Partners", "Clinic Network", "Associates", "Solutions", "Center"]


class MockSearchProvider(SearchProvider):
    name = "offline-sample"

    async def discover_leads(self, icp: dict[str, Any], limit: int = 20) -> list[dict[str, Any]]:
        industry = str(icp.get("industry") or "Business").strip()
        location = str(icp.get("location") or "Unknown").strip()
        company_size = icp.get("company_size")
        keywords = [str(k) for k in icp.get("keywords") or []]
        seed_base = f"{industry}|{location}|{','.join(keywords)}"

        results: list[dict[str, Any]] = []
        for index in range(limit):
            digest = hashlib.sha256(f"{seed_base}|{index}".encode()).hexdigest()
            name_core = (keywords[0] if keywords else industry).title().replace(" ", "")
            company = f"{name_core} {_SUFFIXES[index % len(_SUFFIXES)]} {index + 1}"
            slug = "".join(ch for ch in company.lower() if ch.isalnum())[:24]
            has_contact = index % 3 != 2
            results.append(
                {
                    "company_name": company,
                    "website": f"https://{slug}.example.com",
                    "industry": industry,
                    "location": location,
                    "company_size": str(company_size) if company_size else None,
                    "contact_name": f"Contact {index + 1}" if has_contact else None,
                    "contact_role": "Owner" if has_contact else None,
                    "email": f"hello@{slug}.example.com" if has_contact else None,
                    "phone": None,
                    "linkedin_url": None,
                    "source": self.name,
                    "source_url": f"https://{slug}.example.com",
                    "description": (
                        f"{industry} business in {location} listed by the offline sample provider."
                    ),
                    "_digest": digest[:8],
                }
            )
        return results
