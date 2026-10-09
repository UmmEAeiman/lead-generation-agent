def test_campaign_crud(authed) -> None:
    created = authed.post(
        "/api/v1/campaigns",
        json={
            "name": "Q4 Dental Push",
            "target_industry": "Dental",
            "target_location": "United States",
            "target_company_size": "5-50",
            "keywords": ["dental clinic"],
        },
    )
    assert created.status_code == 201, created.text
    campaign = created.json()
    assert campaign["status"] == "DRAFT"
    assert campaign["keywords"] == ["dental clinic"]

    listed = authed.get("/api/v1/campaigns")
    assert listed.status_code == 200
    assert any(item["id"] == campaign["id"] for item in listed.json()["items"])

    patched = authed.patch(
        f"/api/v1/campaigns/{campaign['id']}", json={"status": "ACTIVE"}
    )
    assert patched.status_code == 200
    assert patched.json()["status"] == "ACTIVE"


def test_campaign_not_found(authed) -> None:
    response = authed.get("/api/v1/campaigns/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CAMPAIGN_NOT_FOUND"
