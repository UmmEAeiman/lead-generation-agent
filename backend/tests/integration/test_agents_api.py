ICP = {
    "industry": "Dental",
    "location": "United States",
    "company_size": "5-50",
    "keywords": ["dental clinic"],
}


def test_discovery_run_creates_leads(authed) -> None:
    queued = authed.post("/api/v1/agents/discovery/run", json={"icp": ICP})
    assert queued.status_code == 202, queued.text
    run_id = queued.json()["run_id"]

    run = authed.get(f"/api/v1/agents/runs/{run_id}").json()
    assert run["status"] == "completed"
    assert run["progress"] == 100
    assert run["output_summary"]["created"] >= 1

    leads = authed.get("/api/v1/leads", params={"page_size": 100}).json()
    assert leads["total"] == run["output_summary"]["created"]

    # Running discovery again must not create duplicates.
    second = authed.post("/api/v1/agents/discovery/run", json={"icp": ICP})
    second_run = authed.get(f"/api/v1/agents/runs/{second.json()['run_id']}").json()
    assert second_run["output_summary"]["duplicates_skipped"] >= 1
    leads_after = authed.get("/api/v1/leads", params={"page_size": 100}).json()
    assert leads_after["total"] == leads["total"]


def test_pipeline_scores_and_personalizes(authed) -> None:
    queued = authed.post("/api/v1/agents/pipeline/run", json={"icp": ICP})
    assert queued.status_code == 202
    run = authed.get(f"/api/v1/agents/runs/{queued.json()['run_id']}").json()
    assert run["status"] == "completed"

    leads = authed.get("/api/v1/leads", params={"page_size": 100}).json()["items"]
    scored = [lead for lead in leads if lead["lead_score"] is not None]
    assert scored, "expected pipeline to score leads"
    assert all(lead["qualification"] in {"low", "medium", "high"} for lead in scored)
    assert all(lead["personalized_message"] for lead in scored)
    assert all(lead["research_summary"] for lead in scored)


def test_enrichment_run_requires_lead_ids(authed) -> None:
    response = authed.post("/api/v1/agents/enrichment/run", json={})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "LEAD_IDS_REQUIRED"


def test_unknown_agent_type(authed) -> None:
    response = authed.post(
        "/api/v1/agents/does-not-exist/run", json={"lead_ids": []}
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "UNKNOWN_AGENT"


def test_single_agent_run_on_existing_lead(authed) -> None:
    created = authed.post("/api/v1/leads", json={"company_name": "Solo Lead Inc"})
    lead_id = created.json()["id"]

    queued = authed.post(
        "/api/v1/agents/qualification/run", json={"lead_ids": [lead_id]}
    )
    assert queued.status_code == 202
    run = authed.get(f"/api/v1/agents/runs/{queued.json()['run_id']}").json()
    assert run["status"] == "completed"
    assert run["output_summary"]["processed"] == 1

    lead = authed.get(f"/api/v1/leads/{lead_id}").json()
    assert lead["lead_score"] is not None
    assert lead["qualification_reasons"]


def test_run_list_scoped_to_user(authed) -> None:
    authed.post("/api/v1/agents/discovery/run", json={"icp": ICP})
    listed = authed.get("/api/v1/agents/runs")
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1

    missing = authed.get("/api/v1/agents/runs/run_does_not_exist")
    assert missing.status_code == 404


def test_discovery_respects_manual_limit(authed) -> None:
    queued = authed.post("/api/v1/agents/discovery/run", json={"icp": ICP, "limit": 2})
    assert queued.status_code == 202, queued.text

    run = authed.get(f"/api/v1/agents/runs/{queued.json()['run_id']}").json()
    assert run["status"] == "completed"
    assert run["output_summary"]["created"] == 2

    leads = authed.get("/api/v1/leads", params={"page_size": 100}).json()
    assert leads["total"] == 2


def test_discovery_limit_validation(authed) -> None:
    too_small = authed.post("/api/v1/agents/discovery/run", json={"icp": ICP, "limit": 0})
    assert too_small.status_code == 422
    too_large = authed.post("/api/v1/agents/discovery/run", json={"icp": ICP, "limit": 51})
    assert too_large.status_code == 422


def test_pipeline_auto_creates_outreach_drafts(authed) -> None:
    queued = authed.post(
        "/api/v1/agents/pipeline/run",
        json={"icp": ICP, "prepare_outreach": True},
    )
    assert queued.status_code == 202, queued.text
    run = authed.get(f"/api/v1/agents/runs/{queued.json()['run_id']}").json()
    assert run["status"] == "completed"
    assert run["input_summary"]["prepare_outreach"] is True
    assert "outreach_drafts" in run["output_summary"]

    leads = authed.get("/api/v1/leads", params={"page_size": 100}).json()["items"]
    eligible = [
        lead
        for lead in leads
        if lead["email"]
        and lead["status"] == "QUALIFIED"
        and lead["personalized_message"]
    ]
    assert run["output_summary"]["outreach_drafts"] == len(eligible)

    outreach = authed.get("/api/v1/outreach", params={"page_size": 100}).json()
    assert outreach["total"] == len(eligible)
    assert all(item["status"] == "PENDING_APPROVAL" for item in outreach["items"])
    # Drafts never auto-send: they still require human approval.
    assert all(item["sent_at"] is None for item in outreach["items"])


def test_pipeline_without_flag_creates_no_drafts(authed) -> None:
    queued = authed.post("/api/v1/agents/pipeline/run", json={"icp": ICP})
    assert queued.status_code == 202
    run = authed.get(f"/api/v1/agents/runs/{queued.json()['run_id']}").json()
    assert run["status"] == "completed"
    assert "outreach_drafts" not in run["output_summary"]
    assert authed.get("/api/v1/outreach", params={"page_size": 100}).json()["total"] == 0

