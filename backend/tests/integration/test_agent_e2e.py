"""End-to-end golden path: a fresh user runs the agent from discovery to a sent email.

This mirrors the manual smoke flow (register -> login -> discovery -> leads ->
pipeline -> outreach prepare/approve/send) as one automated integration test.
The `authed` fixture performs the register + login step on an isolated user.
"""

ICP = {
    "industry": "Dental",
    "location": "Austin, TX",
    "keywords": ["dental clinic"],
}


def test_golden_path_discovery_to_sent_outreach(authed) -> None:
    # 1. Discovery creates leads from the ICP.
    queued = authed.post("/api/v1/agents/discovery/run", json={"icp": ICP})
    assert queued.status_code == 202, queued.text
    discovery = authed.get(f"/api/v1/agents/runs/{queued.json()['run_id']}").json()
    assert discovery["status"] == "completed"
    assert discovery["progress"] == 100
    summary = discovery["output_summary"]
    assert summary["created"] >= 1
    assert summary["provider"] == "offline-sample"
    assert summary["used_llm"] is False

    leads = authed.get("/api/v1/leads", params={"page_size": 100}).json()
    assert leads["total"] == summary["created"]
    discovered_ids = [lead["id"] for lead in leads["items"]]

    # 2. Full pipeline scores, researches and personalizes those leads.
    #    Discovery already created them, so target them explicitly instead of
    #    letting the pipeline rediscover (which would be all duplicates).
    queued = authed.post(
        "/api/v1/agents/pipeline/run", json={"icp": ICP, "lead_ids": discovered_ids}
    )
    assert queued.status_code == 202
    pipeline = authed.get(f"/api/v1/agents/runs/{queued.json()['run_id']}").json()
    assert pipeline["status"] == "completed"
    assert pipeline["output_summary"]["processed"] == len(discovered_ids)
    assert pipeline["output_summary"]["discovery"]["skipped"] is True

    leads = authed.get("/api/v1/leads", params={"page_size": 100}).json()["items"]
    ready = [
        lead
        for lead in leads
        if lead["email"] and lead["personalized_message"] and lead["lead_score"] is not None
    ]
    assert ready, "expected at least one scored, personalized lead with an email"

    # 3. Human approval gate: prepare, approve, then send (local provider).
    lead = ready[0]
    prepared = authed.post("/api/v1/outreach/prepare", json={"lead_id": lead["id"]})
    assert prepared.status_code == 201, prepared.text
    outreach = prepared.json()
    assert outreach["status"] == "PENDING_APPROVAL"

    blocked = authed.post(f"/api/v1/outreach/{outreach['id']}/send")
    assert blocked.status_code == 409
    assert blocked.json()["error"]["code"] == "APPROVAL_REQUIRED"

    approved = authed.post(f"/api/v1/outreach/{outreach['id']}/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "APPROVED"

    sent = authed.post(f"/api/v1/outreach/{outreach['id']}/send")
    assert sent.status_code == 200, sent.text
    assert sent.json()["status"] == "SENT"

    # 4. Lead advanced to CONTACTED and both runs are observable.
    after = authed.get(f"/api/v1/leads/{lead['id']}").json()
    assert after["status"] == "CONTACTED"

    runs = authed.get("/api/v1/agents/runs").json()
    assert runs["total"] >= 2