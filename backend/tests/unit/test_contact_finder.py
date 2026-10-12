"""Unit tests for the free contact-finder integrations (website + Serper)."""

import httpx

from app.agents.enrichment_agent import EnrichmentAgent
from app.core.config import settings
from app.integrations.contact_finder.base import (
    CompositeContactFinder,
    ContactFinder,
    ContactFinderError,
    FoundContact,
)
from app.integrations.contact_finder.factory import get_contact_finder
from app.integrations.contact_finder.serper import SerperContactFinder
from app.integrations.contact_finder.website import WebsiteContactFinder
from app.integrations.email_finder.base import NullEmailFinder

_SAMPLE_HTML = """
<html><body>
  <a href="mailto:john.smith@acme.example">John Smith</a>
  <p>Contact us at info@acme.example or support@gmail.com</p>
</body></html>
"""


def _patch_get(monkeypatch, text, status_code=200):
    captured: dict[str, object] = {}

    async def fake_get(self, url, **kwargs):
        captured["url"] = str(url)
        return httpx.Response(
            status_code, text=text, request=httpx.Request("GET", str(url))
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)
    return captured


def _patch_post(monkeypatch, response_json, status_code=200):
    captured: dict[str, object] = {}

    async def fake_post(self, url, **kwargs):
        captured["url"] = str(url)
        captured["json"] = kwargs.get("json")
        captured["headers"] = kwargs.get("headers") or {}
        return httpx.Response(
            status_code, json=response_json, request=httpx.Request("POST", str(url))
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    return captured


async def test_website_extracts_mailto_and_filters_other_domains(monkeypatch):
    _patch_get(monkeypatch, _SAMPLE_HTML)
    finder = WebsiteContactFinder()

    contacts = await finder.find_contacts(
        domain="acme.example", website="https://acme.example", limit=5
    )

    emails = {c.email: c for c in contacts}
    assert set(emails) == {"john.smith@acme.example", "info@acme.example"}
    assert emails["john.smith@acme.example"].confidence == "verified"
    assert emails["john.smith@acme.example"].full_name == "John Smith"
    assert emails["info@acme.example"].confidence == "unverified"
    assert "support@gmail.com" not in emails


async def test_website_requires_domain():
    finder = WebsiteContactFinder()
    assert await finder.find_contacts(domain="") == []


async def test_serper_contact_finder_parses_snippet(monkeypatch):
    captured = _patch_post(
        monkeypatch,
        {
            "organic": [
                {
                    "title": "Contact Acme",
                    "link": "https://acme.example/contact",
                    "snippet": "Reach us at hello@acme.example",
                }
            ]
        },
    )
    finder = SerperContactFinder(api_key="k")

    contacts = await finder.find_contacts(domain="acme.example", company_name="Acme")

    assert captured["url"].endswith("/search")
    assert captured["headers"]["X-API-KEY"] == "k"
    assert [c.email for c in contacts] == ["hello@acme.example"]
    assert contacts[0].source == "serper"
    assert contacts[0].confidence == "unverified"


async def test_serper_contact_finder_missing_key_raises():
    finder = SerperContactFinder(api_key="")
    try:
        await finder.find_contacts(domain="acme.example")
    except ContactFinderError:
        pass
    else:  # pragma: no cover - guard
        raise AssertionError("expected ContactFinderError")


class _StubFinder(ContactFinder):
    name = "stub"
    is_configured = True

    def __init__(self, contacts):
        self._contacts = contacts

    async def find_contacts(self, *, domain, company_name=None, website=None, limit=5):
        return list(self._contacts)


async def test_composite_dedupes_by_email():
    shared = FoundContact(email="info@acme.example", source="a")
    composite = CompositeContactFinder(
        [
            _StubFinder([shared, FoundContact(email="jane@acme.example", source="a")]),
            _StubFinder([shared, FoundContact(email="bob@acme.example", source="b")]),
        ]
    )

    contacts = await composite.find_contacts(domain="acme.example", limit=10)

    assert [c.email for c in contacts] == [
        "info@acme.example",
        "jane@acme.example",
        "bob@acme.example",
    ]


def test_contact_finder_factory_toggle(monkeypatch):
    monkeypatch.setattr(settings, "contact_finder_enabled", False)
    assert get_contact_finder().name == "none"

    monkeypatch.setattr(settings, "contact_finder_enabled", True)
    assert get_contact_finder().name == "composite"


def test_best_contact_prefers_non_generic():
    contacts = [
        FoundContact(email="info@acme.example", source="w"),
        FoundContact(email="jane@acme.example", source="w", confidence="verified"),
    ]
    best = EnrichmentAgent._best_contact(contacts)
    assert best is not None
    assert best.email == "jane@acme.example"


async def test_enrichment_uses_contact_finder():
    stub = _StubFinder(
        [
            FoundContact(
                email="jane@bright.example",
                full_name="Jane Doe",
                role="ceo",
                source="stub",
                confidence="verified",
            )
        ]
    )
    agent = EnrichmentAgent(email_finder=NullEmailFinder(), contact_finder=stub)

    result = await agent.run(
        {"company_name": "Bright", "website": "https://bright.example"}
    )

    assert result.fields["email"] == "jane@bright.example"
    assert result.fields["contact_name"] == "Jane Doe"
    assert result.fields["contact_role"] == "ceo"
    assert result.field_confidence["email"] == "verified"
