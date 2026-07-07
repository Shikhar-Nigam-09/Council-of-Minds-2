import os

import pytest
from fastapi.testclient import TestClient

# Configure isolated test database
os.environ["BACKEND_DATABASE_URL"] = "sqlite+aiosqlite:///./test_settings.db"
os.environ["BACKEND_ENVIRONMENT"] = "testing"

import asyncio
import uuid

from app.core.database import Base, engine
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def setup_settings_db():
    """Setup and teardown isolated test database for settings tests."""

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    yield


@pytest.fixture(scope="module")
def auth_headers():
    """Register and login a user to get auth headers."""
    reg_payload = {
        "email": "settingsuser@example.com",
        "password": "Password123!",
        "full_name": "Settings User",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "settingsuser@example.com", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_settings_default(auth_headers):
    """Test getting user settings returns profile and sensible default agent weights."""
    response = client.get("/api/v1/settings", headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "settingsuser@example.com"
    assert data["full_name"] == "Settings User"
    assert data["agent_weights"] == {
        "logical": 1.0,
        "rational": 1.0,
        "practical": 1.0,
        "spiritual": 1.0,
        "skeptical": 1.0,
    }


def test_update_profile(auth_headers):
    """Test updating user profile display name."""
    response = client.patch(
        "/api/v1/settings/profile",
        json={"full_name": "Updated Name"},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["full_name"] == "Updated Name"

    # Verify persistence
    get_res = client.get("/api/v1/settings", headers=auth_headers)
    assert get_res.json()["full_name"] == "Updated Name"


def test_update_agent_weights_success(auth_headers):
    """Test updating agent weights successfully."""
    new_weights = {
        "logical": 2.0,
        "rational": 0.5,
        "practical": 1.5,
        "spiritual": 0.0,
        "skeptical": 3.0,
    }
    response = client.patch(
        "/api/v1/settings/agent-weights",
        json={"agent_weights": new_weights},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["agent_weights"] == new_weights


def test_update_agent_weights_invalid_missing_agent(auth_headers):
    """Test updating agent weights missing a required persona returns 400."""
    invalid_weights = {
        "logical": 1.0,
        "rational": 1.0,
        "practical": 1.0,
        "spiritual": 1.0,
        # missing skeptical
    }
    response = client.patch(
        "/api/v1/settings/agent-weights",
        json={"agent_weights": invalid_weights},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "exactly" in response.json()["detail"].lower()


def test_update_agent_weights_invalid_unknown_agent(auth_headers):
    """Test updating agent weights with unknown persona key returns 400."""
    invalid_weights = {
        "logical": 1.0,
        "rational": 1.0,
        "practical": 1.0,
        "spiritual": 1.0,
        "skeptical": 1.0,
        "rogue_agent": 5.0,
    }
    response = client.patch(
        "/api/v1/settings/agent-weights",
        json={"agent_weights": invalid_weights},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_update_agent_weights_invalid_negative(auth_headers):
    """Test updating agent weights with negative numbers returns 400."""
    invalid_weights = {
        "logical": -1.0,
        "rational": 1.0,
        "practical": 1.0,
        "spiritual": 1.0,
        "skeptical": 1.0,
    }
    response = client.patch(
        "/api/v1/settings/agent-weights",
        json={"agent_weights": invalid_weights},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "non-negative" in response.json()["detail"].lower()


def test_update_agent_weights_invalid_all_zero(auth_headers):
    """Test updating agent weights with all zeroes returns 400."""
    invalid_weights = {
        "logical": 0.0,
        "rational": 0.0,
        "practical": 0.0,
        "spiritual": 0.0,
        "skeptical": 0.0,
    }
    response = client.patch(
        "/api/v1/settings/agent-weights",
        json={"agent_weights": invalid_weights},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "greater than 0" in response.json()["detail"].lower()


def test_password_change_invalidates_settings_access():
    """Test that changing password invalidates existing sessions when accessing settings."""
    # 1. Register and login
    reg_payload = {
        "email": "pwuser@example.com",
        "password": "OldPassword123!",
        "full_name": "Password User",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "pwuser@example.com", "password": "OldPassword123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Verify access to settings
    assert client.get("/api/v1/settings", headers=headers).status_code == 200

    # 3. Change password
    pw_res = client.post(
        "/api/v1/auth/change-password",
        json={
            "old_password": "OldPassword123!",
            "new_password": "NewPassword456!",
        },
        headers=headers,
    )
    assert pw_res.status_code == 200

    # 4. Verify old token now fails with 401 on /api/v1/settings
    fail_res = client.get("/api/v1/settings", headers=headers)
    assert fail_res.status_code == 401


def test_paginated_document_chunks_endpoint(auth_headers):
    """Test paginated chunks endpoint on non-existent document returns 404."""
    random_id = str(uuid.uuid4())
    res = client.get(
        f"/api/v1/documents/{random_id}/chunks?page=1&page_size=10",
        headers=auth_headers,
    )
    assert res.status_code == 404
