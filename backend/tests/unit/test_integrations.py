"""Unit tests for the external provider integrations (email + search)."""

import httpx

from app.agents.enrichment_agent import EnrichmentAgent
from app.core.config import settings
from app.integrations.email.base import EmailProviderError
from app.integrations.email.factory import get_email_provider
from app.integrations.email.resend import ResendEmailProvider
from app.integrations.email.smtp import SmtpEmailProvider
from app.integrations.email_finder.base import EmailFinderError, FoundEmail
from app.integrations.email_finder.enrich import EnrichEmailFinder
from app.integrations.email_finder.factory import get_email_finder
from app.integrations.email_finder.hunter import HunterEmailFinder
from app.integrations.search.base import SearchProviderError
from app.integrations.search.factory import get_search_provider
from app.integrations.search.serper import SerperSearchProvider


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


async def test_serper_places_maps_local_business(monkeypatch):
    captured = _patch_post(
        monkeypatch,
        {
            "places": [
                {
                    "title": "Bright Dental",
                    "address": "1 Main St, Austin, TX",
                    "phoneNumber": "555-1234",
                    "website": "https://bright.example",
                    "category": "Dentist",
                    "rating": 4.7,
                    "ratingCount": 120,
                }
            ]
        },
    )
    icp = {"industry": "Dental", "location": "Austin, TX", "keywords": ["dental clinic"]}
    provider = SerperSearchProvider(api_key="k")

    leads = await provider.discover_leads(icp, limit=5)

    assert captured["url"].endswith("/places")
    assert "Austin" in captured["json"]["q"]
    assert captured["headers"]["X-API-KEY"] == "k"
    assert len(leads) == 1
    lead = leads[0]
    assert lead["company_name"] == "Bright Dental"
    assert lead["website"] == "https://bright.example"
    assert lead["phone"] == "555-1234"
    assert lead["location"] == "1 Main St, Austin, TX"
    assert lead["industry"] == "Dentist"
    assert lead["source"] == "serper"
    assert lead["contact_name"] is None
    assert lead["email"] is None


async def test_serper_search_used_without_location(monkeypatch):
    captured = _patch_post(
        monkeypatch,
        {
            "organic": [
                {"title": "Acme CRM", "link": "https://acme.example", "snippet": "CRM tools"}
            ]
        },
    )
    provider = SerperSearchProvider(api_key="k")

    leads = await provider.discover_leads({"industry": "SaaS", "keywords": ["crm"]}, limit=3)

    assert captured["url"].endswith("/search")
    assert captured["json"]["num"] == 3
    assert leads[0]["company_name"] == "Acme CRM"
    assert leads[0]["website"] == "https://acme.example"
    assert leads[0]["description"] == "CRM tools"
    assert leads[0]["source"] == "serper"


async def test_serper_missing_key_raises(monkeypatch):
    provider = SerperSearchProvider(api_key="")
    try:
        await provider.discover_leads({"industry": "Dental"}, limit=1)
    except SearchProviderError:
        pass
    else:  # pragma: no cover - guard
        raise AssertionError("expected SearchProviderError")


async def test_resend_sends_email(monkeypatch):
    captured = _patch_post(monkeypatch, {"id": "msg-123"})
    provider = ResendEmailProvider(api_key="k", sender="sender@example.com", sender_name="LeadGen")

    message_id = await provider.send_email(to="lead@example.com", subject="Hi", body="Hello there")

    assert message_id == "msg-123"
    assert captured["url"].endswith("/emails")
    assert captured["headers"]["Authorization"] == "Bearer k"
    assert captured["json"]["to"] == ["lead@example.com"]
    assert captured["json"]["subject"] == "Hi"
    assert captured["json"]["text"] == "Hello there"
    assert captured["json"]["from"] == "LeadGen <sender@example.com>"


async def test_resend_missing_key_raises():
    provider = ResendEmailProvider(api_key="")
    try:
        await provider.send_email(to="lead@example.com", subject="Hi", body="Hello")
    except EmailProviderError:
        pass
    else:  # pragma: no cover - guard
        raise AssertionError("expected EmailProviderError")


async def test_resend_http_error_raises(monkeypatch):
    _patch_post(monkeypatch, {"message": "nope"}, status_code=422)
    provider = ResendEmailProvider(api_key="k")
    try:
        await provider.send_email(to="lead@example.com", subject="Hi", body="Hello")
    except EmailProviderError:
        pass
    else:  # pragma: no cover - guard
        raise AssertionError("expected EmailProviderError")


async def test_smtp_sends_email(monkeypatch):
    sent: dict[str, object] = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout=None):
            sent["host"] = host
            sent["port"] = port

        def ehlo(self):
            pass

        def starttls(self):
            sent["starttls"] = True

        def login(self, user, password):
            sent["login"] = (user, password)

        def send_message(self, message):
            sent["message"] = message

        def quit(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr("app.integrations.email.smtp.smtplib.SMTP", FakeSMTP)

    provider = SmtpEmailProvider(
        host="smtp.example.com",
        port=587,
        username="user",
        password="secret",
        sender="sender@example.com",
        sender_name="LeadGen",
        use_tls=True,
    )

    message_id = await provider.send_email(to="lead@example.com", subject="Hi", body="Hello")

    assert message_id
    assert sent["host"] == "smtp.example.com"
    assert sent["port"] == 587
    assert sent["starttls"] is True
    assert sent["login"] == ("user", "secret")
    message = sent["message"]
    assert message["To"] == "lead@example.com"
    assert message["Subject"] == "Hi"
    assert "sender@example.com" in message["From"]


async def test_smtp_missing_config_raises():
    provider = SmtpEmailProvider(host="")
    try:
        await provider.send_email(to="lead@example.com", subject="Hi", body="Hello")
    except EmailProviderError:
        pass
    else:  # pragma: no cover - guard
        raise AssertionError("expected EmailProviderError")


def test_factories_fall_back_to_local_and_mock():
    assert settings.email_provider == "local"
    assert settings.search_provider == "mock"
    assert get_email_provider().name == "local"
    assert get_search_provider().name == "offline-sample"


def test_factories_select_live_providers_when_configured(monkeypatch):
    monkeypatch.setattr(settings, "email_provider", "resend")
    monkeypatch.setattr(settings, "email_api_key", "k")
    monkeypatch.setattr(settings, "search_provider", "serper")
    monkeypatch.setattr(settings, "search_api_key", "k")

    assert get_email_provider().name == "resend"
    assert get_search_provider().name == "serper"


def test_factory_selects_smtp_when_configured(monkeypatch):
    monkeypatch.setattr(settings, "email_provider", "smtp")
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.com")
    monkeypatch.setattr(settings, "email_from", "sender@example.com")

    assert get_email_provider().name == "smtp"


def _patch_get(monkeypatch, response_json, status_code=200):
    captured: dict[str, object] = {}

    async def fake_get(self, url, **kwargs):
        captured["url"] = str(url)
        captured["params"] = kwargs.get("params") or {}
        return httpx.Response(
            status_code, json=response_json, request=httpx.Request("GET", str(url))
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)
    return captured


async def test_hunter_domain_search_picks_highest_confidence(monkeypatch):
    captured = _patch_get(
        monkeypatch,
        {
            "data": {
                "emails": [
                    {"value": "info@acme.example", "confidence": 40},
                    {
                        "value": "jane@acme.example",
                        "confidence": 92,
                        "verification": {"status": "valid"},
                    },
                ]
            }
        },
    )
    provider = HunterEmailFinder(api_key="k")

    found = await provider.find_email(domain="acme.example")

    assert captured["url"].endswith("/domain-search")
    assert captured["params"]["domain"] == "acme.example"
    assert captured["params"]["api_key"] == "k"
    assert found is not None
    assert found.email == "jane@acme.example"
    assert found.score == 92
    assert found.confidence == "verified"
    assert found.source == "hunter"


async def test_hunter_email_finder_uses_contact_name(monkeypatch):
    captured = _patch_get(
        monkeypatch,
        {
            "data": {
                "email": "jane@acme.example",
                "score": 80,
                "verification": {"status": "accept_all"},
            }
        },
    )
    provider = HunterEmailFinder(api_key="k")

    found = await provider.find_email(
        domain="acme.example", first_name="Jane", last_name="Doe"
    )

    assert captured["url"].endswith("/email-finder")
    assert captured["params"]["first_name"] == "Jane"
    assert captured["params"]["last_name"] == "Doe"
    assert found is not None
    assert found.email == "jane@acme.example"
    assert found.confidence == "unverified"


async def test_hunter_missing_key_raises():
    provider = HunterEmailFinder(api_key="")
    try:
        await provider.find_email(domain="acme.example")
    except EmailFinderError:
        pass
    else:  # pragma: no cover - guard
        raise AssertionError("expected EmailFinderError")


def test_email_finder_factory_disabled_without_key(monkeypatch):
    monkeypatch.setattr(settings, "email_finder_provider", "hunter")
    monkeypatch.setattr(settings, "hunter_api_key", None)
    assert get_email_finder().name == "none"

    monkeypatch.setattr(settings, "hunter_api_key", "k")
    assert get_email_finder().name == "hunter"


async def test_enrichment_uses_email_finder():
    class StubFinder:
        is_configured = True

        async def find_email(self, *, domain, first_name=None, last_name=None):
            assert domain == "bright.example"
            return FoundEmail(
                email="hello@bright.example",
                source="stub",
                score=95,
                confidence="verified",
            )

    agent = EnrichmentAgent(email_finder=StubFinder())
    result = await agent.run({"company_name": "Bright", "website": "https://bright.example"})

    assert result.fields["email"] == "hello@bright.example"
    assert result.field_confidence["email"] == "verified"


async def test_enrich_email_finder_returns_email(monkeypatch):
    captured = _patch_post(
        monkeypatch,
        {
            "success": True,
            "data": {
                "email": "jane@acme.example",
                "confidence": "high",
                "score": 96,
                "verified": True,
            },
            "meta": {"creditsUsed": 10, "creditsRemaining": 90},
        },
    )
    provider = EnrichEmailFinder(api_key="sk_test")

    found = await provider.find_email(
        domain="acme.example", first_name="Jane", last_name="Doe"
    )

    assert captured["url"].endswith("/api/v3/email-finder")
    assert captured["headers"]["x-api-key"] == "sk_test"
    assert captured["json"] == {
        "firstName": "Jane",
        "lastName": "Doe",
        "domain": "acme.example",
    }
    assert found is not None
    assert found.email == "jane@acme.example"
    assert found.score == 96
    assert found.confidence == "verified"
    assert found.source == "enrich"


async def test_enrich_requires_full_name(monkeypatch):
    captured = _patch_post(monkeypatch, {"success": True})
    provider = EnrichEmailFinder(api_key="k")

    assert await provider.find_email(domain="acme.example") is None
    assert await provider.find_email(domain="acme.example", first_name="Jane") is None
    assert "url" not in captured


async def test_enrich_missing_key_raises():
    provider = EnrichEmailFinder(api_key="")
    try:
        await provider.find_email(domain="acme.example", first_name="A", last_name="B")
    except EmailFinderError:
        pass
    else:  # pragma: no cover - guard
        raise AssertionError("expected EmailFinderError")


def test_email_finder_factory_selects_enrich(monkeypatch):
    monkeypatch.setattr(settings, "email_finder_provider", "enrich")
    monkeypatch.setattr(settings, "enrich_api_key", "k")
    assert get_email_finder().name == "enrich"

    monkeypatch.setattr(settings, "enrich_api_key", None)
    assert get_email_finder().name == "none"