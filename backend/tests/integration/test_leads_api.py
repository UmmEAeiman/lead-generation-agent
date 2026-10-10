def test_lead_crud_and_filters(authed) -> None:
    created = authed.post(
        "/api/v1/leads",
        json={
            "company_name": "Acme Dental",
            "industry": "Dental",
            "location": "Texas",
            "email": "hello@acme-dental.example.com",
            "website": "acme-dental.example.com",
        },
    )
    assert created.status_code == 201, created.text
    lead = created.json()
    assert lead["email"] == "hello@acme-dental.example.com"
    assert lead["website"] == "https://acme-dental.example.com"
    assert lead["status"] == "NEW"

    fetched = authed.get(f"/api/v1/leads/{lead['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["company_name"] == "Acme Dental"

    filtered = authed.get("/api/v1/leads", params={"q": "Acme", "industry": "Dental"})
    assert filtered.status_code == 200
    page = filtered.json()
    assert page["total"] >= 1
    assert any(item["id"] == lead["id"] for item in page["items"])

    patched = authed.patch(
        f"/api/v1/leads/{lead['id']}",
        json={"status": "ENRICHING"},
    )
    assert patched.status_code == 200
    assert patched.json()["status"] == "ENRICHING"


def test_duplicate_lead_rejected(authed) -> None:
    payload = {
        "company_name": "Dup Corp",
        "website": "https://dupcorp.example.com",
        "email": "team@dupcorp.example.com",
    }
    assert authed.post("/api/v1/leads", json=payload).status_code == 201
    duplicate = authed.post(
        "/api/v1/leads",
        json={"company_name": "Dup Corp Again", "website": "dupcorp.example.com"},
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "DUPLICATE_LEAD"


def test_invalid_status_transition_rejected(authed) -> None:
    created = authed.post("/api/v1/leads", json={"company_name": "Fresh Lead"})
    lead_id = created.json()["id"]
    response = authed.patch(f"/api/v1/leads/{lead_id}", json={"status": "MEETING_BOOKED"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_STATUS_TRANSITION"


def test_lead_not_found(authed) -> None:
    response = authed.get("/api/v1/leads/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "LEAD_NOT_FOUND"


def test_opt_out_blocks_outreach(authed) -> None:
    created = authed.post(
        "/api/v1/leads",
        json={"company_name": "Opted Out Co", "email": "bye@optout.example.com"},
    )
    lead_id = created.json()["id"]

    assert authed.post(f"/api/v1/leads/{lead_id}/opt-out").status_code == 204
    after = authed.get(f"/api/v1/leads/{lead_id}").json()
    assert after["status"] == "DO_NOT_CONTACT"
    assert after["followup_state"] == "DO_NOT_CONTACT"

    transition = authed.patch(f"/api/v1/leads/{lead_id}", json={"status": "CONTACTED"})
    assert transition.status_code == 422


def test_similar_lead_search(authed) -> None:
    authed.post(
        "/api/v1/leads",
        json={
            "company_name": "Sunrise Orthodontics",
            "industry": "Orthodontics",
            "description": "orthodontic care for children",
        },
    )
    response = authed.get("/api/v1/leads/search", params={"q": "orthodontic care"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_export_leads_csv(authed) -> None:
    authed.post(
        "/api/v1/leads",
        json={
            "company_name": "CSV Export Co",
            "industry": "Retail",
            "email": "csv@export.example.com",
        },
    )
    response = authed.get("/api/v1/leads/export", params={"q": "CSV Export"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]
    body = response.content.decode("utf-8-sig")
    assert "company_name" in body
    assert "CSV Export Co" in body
