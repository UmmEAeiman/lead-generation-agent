"""Unit tests for the external provider integrations (email + search)."""

import httpx

from app.core.config import settings
from app.integrations.email.base import EmailProviderError
from app.integrations.email.factory import get_email_provider
from app.integrations.email.resend import ResendEmailProvider
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