import os

import pytest
from fastapi.testclient import TestClient

# Configure isolated test database
os.environ["BACKEND_DATABASE_URL"] = "sqlite+aiosqlite:///./test_auth.db"
os.environ["BACKEND_ENVIRONMENT"] = "testing"

import asyncio

from app.core.database import Base, engine
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def setup_test_db():
    """Setup and teardown isolated test database for authentication tests."""

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    yield


def test_register_success():
    """Test successful user registration creates user and default settings."""
    payload = {
        "email": "testuser@example.com",
        "password": "Password123!",
        "full_name": "Test User",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["token_version"] == 0
    assert data["is_active"] is True
    assert data["settings"] is not None
    assert "agent_weights" in data["settings"]
    assert data["settings"]["agent_weights"]["logical"] == 1.0


def test_register_duplicate():
    """Test registering an existing email returns 409 Conflict."""
    payload = {
        "email": "testuser@example.com",
        "password": "Password123!",
        "full_name": "Test User",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


def test_login_success():
    """Test successful login issues valid JWT access and refresh tokens."""
    payload = {"email": "testuser@example.com", "password": "Password123!"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password():
    """Test login with incorrect password returns 401 Unauthorized."""
    payload = {"email": "testuser@example.com", "password": "WrongPassword!"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401


def test_get_me_protected():
    """Test accessing protected /me endpoint with valid access token."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "testuser@example.com", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["token_version"] == 0


def test_get_me_unauthorized():
    """Test accessing protected /me endpoint with invalid or missing token returns 401."""
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token_str"}
    )
    assert response.status_code == 401
