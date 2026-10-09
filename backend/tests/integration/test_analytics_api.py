def test_overview_starts_empty(authed) -> None:
    response = authed.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    body = response.json()
    assert body["total_leads"] == 0
    assert body["qualification_rate"] == 0.0


def test_overview_after_activity(authed) -> None:
    campaign = authed.post(
        "/api/v1/campaigns",
        json={"name": "Analytics Campaign", "target_industry": "Dental"},
    ).json()

    queued = authed.post(
        "/api/v1/agents/pipeline/run",
        json={"campaign_id": campaign["id"], "icp": {"industry": "Dental"}},
    )
    assert queued.status_code == 202
    run = authed.get(f"/api/v1/agents/runs/{queued.json()['run_id']}").json()
    assert run["status"] == "completed"

    leads = authed.get("/api/v1/leads", params={"page_size": 100}).json()["items"]
    assert leads
    target = leads[0]
    authed.patch(f"/api/v1/leads/{target['id']}", json={"status": "ENRICHING"})
    if target["lead_score"] is not None and target["lead_score"] >= 40:
        authed.patch(f"/api/v1/leads/{target['id']}", json={"status": "QUALIFIED"})
        authed.patch(f"/api/v1/leads/{target['id']}", json={"status": "CONTACTED"})

    overview = authed.get("/api/v1/analytics/overview").json()
    assert overview["total_leads"] == len(leads)
    assert overview["agent_runs_total"] >= 1
    assert overview["agent_runs_failed"] == 0
    assert overview["agent_success_rate"] == 100.0
    assert overview["campaign_performance"], "expected campaign rows"
    campaign_row = overview["campaign_performance"][0]
    assert campaign_row["name"] == "Analytics Campaign"
    assert campaign_row["total_leads"] == len(leads)
