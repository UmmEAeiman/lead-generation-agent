import asyncio

from app.agents.discovery_agent import DiscoveryAgent
from app.agents.enrichment_agent import EnrichmentAgent
from app.agents.followup_agent import FollowupAgent, state_from_lead_status
from app.agents.personalization_agent import PersonalizationAgent
from app.agents.research_agent import ResearchAgent
from app.models.enums import FollowupState, LeadStatus

ICP = {"industry": "Dental", "location": "United States", "keywords": ["dental clinic"]}


def test_discovery_returns_leads_with_provider() -> None:
    agent = DiscoveryAgent()
    result = asyncio.run(agent.run(ICP, limit=5))
    assert result.selected == 5
    assert result.provider == "offline-sample"
    assert all(lead["company_name"] for lead in result.leads)
    assert result.used_llm is False


def test_enrichment_fallback_marks_confidence() -> None:
    agent = EnrichmentAgent()
    result = asyncio.run(
        agent.run({"company_name": "Acme", "website": "acme.com", "email": None})
    )
    assert result.fields["website"] == "https://acme.com"
    assert result.field_confidence["website"] == "verified"
    assert result.field_confidence["email"] == "unknown"
    assert result.used_llm is False


def test_research_fallback_does_not_invent() -> None:
    agent = ResearchAgent()
    result = asyncio.run(agent.run({"company_name": "Acme", "website": None}))
    assert "LLM research not configured" in result.summary
    assert all(f["confidence"] in {"verified", "unknown"} for f in result.findings)
    assert result.pain_points == []


def test_personalization_fallback_uses_only_known_facts() -> None:
    agent = PersonalizationAgent()
    result = asyncio.run(
        agent.run(
            {"company_name": "Acme Dental", "industry": "Dental", "contact_name": None},
            research_summary="",
            pain_points=[],
        )
    )
    assert "Acme Dental" in result.message
    assert "Dental" in result.message
    assert "[" not in result.message
    assert result.used_llm is False
    assert any("contact name" in f for f in result.omitted_info)


def test_followup_stops_on_do_not_contact() -> None:
    agent = FollowupAgent()
    result = asyncio.run(agent.run({}, FollowupState.DO_NOT_CONTACT.value))
    assert result.action == "stop"
    assert result.message is None


def test_followup_nudges_on_no_response() -> None:
    agent = FollowupAgent()
    result = asyncio.run(agent.run({}, FollowupState.NO_RESPONSE.value))
    assert result.action == "follow_up"
    assert result.message


def test_state_from_lead_status() -> None:
    dnc = FollowupState.DO_NOT_CONTACT.value
    assert state_from_lead_status(LeadStatus.DO_NOT_CONTACT.value) == dnc
    assert state_from_lead_status(LeadStatus.CONTACTED.value) == FollowupState.NO_RESPONSE.value
    assert state_from_lead_status("UNKNOWN_STATUS") == FollowupState.NO_RESPONSE.value
