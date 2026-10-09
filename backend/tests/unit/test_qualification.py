from app.agents.qualification_agent import DEFAULT_CRITERIA, band_for_score, score_lead


def test_band_boundaries() -> None:
    assert band_for_score(0) == "low"
    assert band_for_score(39) == "low"
    assert band_for_score(40) == "medium"
    assert band_for_score(69) == "medium"
    assert band_for_score(70) == "high"
    assert band_for_score(100) == "high"


def test_criteria_sums_to_100() -> None:
    assert DEFAULT_CRITERIA.total == 100


def test_scoring_without_icp_is_conservative() -> None:
    result = score_lead({"company_name": "Acme"}, icp={}, research={})
    assert 0 <= result.score <= 100
    assert result.category == "low"
    assert any("No ICP industry defined" in reason for reason in result.reasons)


def test_scoring_full_match_scores_high() -> None:
    lead = {
        "company_name": "Acme Dental Clinic",
        "industry": "Dental",
        "location": "United States",
        "company_size": "5-50",
        "email": "hi@acme.com",
        "contact_name": "Jane",
        "contact_role": "Owner",
        "description": "dental clinic practice",
    }
    icp = {
        "industry": "Dental",
        "location": "United States",
        "company_size": "5-50",
        "keywords": ["dental clinic"],
    }
    research = {"buying_signals": ["pricing page visit"], "pain_points": ["no online booking"]}
    result = score_lead(lead, icp, research)
    assert result.score >= 70
    assert result.category == "high"
    assert sum(result.breakdown.values()) == result.score
    for key, cap in DEFAULT_CRITERIA.caps.items():
        assert result.breakdown[key] <= cap


def test_score_never_exceeds_100() -> None:
    lead = {
        "company_name": "Acme",
        "industry": "Dental",
        "location": "United States",
        "company_size": "5-50",
        "email": "a@b.com",
        "contact_name": "A",
        "contact_role": "Owner",
    }
    icp = {"industry": "Dental", "location": "United States", "company_size": "5-50"}
    research = {"buying_signals": ["s1", "s2", "s3", "s4"], "pain_points": ["p1"]}
    result = score_lead(lead, icp, research)
    assert result.score <= 100
