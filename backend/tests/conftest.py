# ruff: noqa: E402
"""Test bootstrap: isolate the database before the app engine is created."""

import os
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUTO_CREATE_TABLES"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key-0123456789abcdef0123456789abcdef"

# Keep tests hermetic: force offline providers regardless of backend/.env, so the
# suite never spends Serper/Groq credits or sends real email during a test run.
os.environ["LLM_PROVIDER"] = "groq"
os.environ["GROQ_API_KEY"] = ""
os.environ["SEARCH_PROVIDER"] = "mock"
os.environ["SEARCH_API_KEY"] = ""
os.environ["EMAIL_PROVIDER"] = "local"
os.environ["EMAIL_API_KEY"] = ""

import pytest
from fastapi.testclient import TestClient

from app.main import app

PASSWORD = "password123"


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def authed(client: TestClient) -> TestClient:
    """Client logged in as a fresh, isolated user for this test."""
    email = f"test-{uuid4().hex[:12]}@example.com"
    registered = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": PASSWORD, "full_name": "Test User"},
    )
    assert registered.status_code == 201, registered.text
    logged_in = client.post(
        "/api/v1/auth/login", json={"email": email, "password": PASSWORD}
    )
    assert logged_in.status_code == 200, logged_in.text
    client.email = email  # type: ignore[attr-defined]
    return client
