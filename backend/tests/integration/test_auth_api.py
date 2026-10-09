from uuid import uuid4


def test_register_login_me_logout(client) -> None:
    email = f"auth-{uuid4().hex[:10]}@example.com"
    registered = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "full_name": "Ada"},
    )
    assert registered.status_code == 201
    assert registered.json()["email"] == email

    wrong = client.post("/api/v1/auth/login", json={"email": email, "password": "nope"})
    assert wrong.status_code == 401
    assert wrong.json()["error"]["code"] == "INVALID_CREDENTIALS"

    logged_in = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "password123"}
    )
    assert logged_in.status_code == 200

    me = client.get("/api/v1/users/me")
    assert me.status_code == 200
    assert me.json()["email"] == email

    assert client.post("/api/v1/auth/logout").status_code == 204


def test_duplicate_registration_conflicts(client) -> None:
    email = f"dup-{uuid4().hex[:10]}@example.com"
    payload = {"email": email, "password": "password123"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    second = client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "EMAIL_TAKEN"


def test_me_requires_auth(client) -> None:
    client.post("/api/v1/auth/logout")
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_validation_error_shape(client) -> None:
    response = client.post("/api/v1/auth/register", json={"email": "not-an-email"})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
