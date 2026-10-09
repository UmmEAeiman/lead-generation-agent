def _create_lead(client, company="Outreach Co"):
    email_domain = company.lower().replace(" ", "")
    response = client.post(
        "/api/v1/leads",
        json={"company_name": company, "email": f"hi@{email_domain}.example.com"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_full_outreach_flow(authed) -> None:
    lead = _create_lead(authed, "Flow Corp")

    early = authed.post("/api/v1/outreach/prepare", json={"lead_id": lead["id"]})
    assert early.status_code == 409
    assert early.json()["error"]["code"] == "NO_MESSAGE"

    queued = authed.post(
        "/api/v1/agents/personalization/run", json={"lead_ids": [lead["id"]]}
    )
    assert queued.status_code == 202
    run = authed.get(f"/api/v1/agents/runs/{queued.json()['run_id']}").json()
    assert run["status"] == "completed"

    prepared = authed.post("/api/v1/outreach/prepare", json={"lead_id": lead["id"]})
    assert prepared.status_code == 201, prepared.text
    outreach = prepared.json()
    assert outreach["status"] == "PENDING_APPROVAL"
    assert outreach["body"]

    early_send = authed.post(f"/api/v1/outreach/{outreach['id']}/send")
    assert early_send.status_code == 409
    assert early_send.json()["error"]["code"] == "APPROVAL_REQUIRED"

    approved = authed.post(f"/api/v1/outreach/{outreach['id']}/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "APPROVED"

    sent = authed.post(f"/api/v1/outreach/{outreach['id']}/send")
    assert sent.status_code == 200, sent.text
    assert sent.json()["status"] == "SENT"

    after = authed.get(f"/api/v1/leads/{lead['id']}").json()
    assert after["status"] == "CONTACTED"


def test_opt_out_blocks_new_outreach(authed) -> None:
    lead = _create_lead(authed, "No Contact Co")
    authed.post(
        "/api/v1/agents/personalization/run", json={"lead_ids": [lead["id"]]}
    )
    assert authed.post(f"/api/v1/leads/{lead['id']}/opt-out").status_code == 204

    blocked = authed.post("/api/v1/outreach/prepare", json={"lead_id": lead["id"]})
    assert blocked.status_code == 403
    assert blocked.json()["error"]["code"] == "OPTED_OUT"


def test_outreach_list(authed) -> None:
    listed = authed.get("/api/v1/outreach")
    assert listed.status_code == 200
    assert set(listed.json().keys()) == {"items", "total", "page", "page_size"}
