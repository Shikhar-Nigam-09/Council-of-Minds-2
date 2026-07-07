import os

import pytest
from fastapi.testclient import TestClient

# Configure isolated test database
os.environ["BACKEND_DATABASE_URL"] = "sqlite+aiosqlite:///./test_versioning.db"
os.environ["BACKEND_ENVIRONMENT"] = "testing"

import asyncio

from app.core.database import Base, engine
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def setup_versioning_db():
    """Setup and teardown isolated test database for token versioning tests."""

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    yield


def test_token_invalidation_on_password_change():
    """Test that changing password increments token_version and immediately invalidates all prior tokens."""
    # 1. Register a user for versioning test
    reg_payload = {
        "email": "versionuser@example.com",
        "password": "OldPassword123!",
        "full_name": "Version User",
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201

    # 2. Login to get initial tokens (version 0)
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "versionuser@example.com",
            "password": "OldPassword123!",
        },
    )
    assert login_res.status_code == 200
    tokens = login_res.json()
    old_access_token = tokens["access_token"]
    old_refresh_token = tokens["refresh_token"]

    # Verify old access token works on /me
    me_res = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {old_access_token}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["token_version"] == 0

    # 3. Verify refresh endpoint works with old refresh token before password change
    ref_res = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": old_refresh_token}
    )
    assert ref_res.status_code == 200
    new_tokens = ref_res.json()
    current_access = new_tokens["access_token"]
    current_refresh = new_tokens["refresh_token"]

    # 4. Change password using current access token
    pw_res = client.post(
        "/api/v1/auth/change-password",
        json={
            "old_password": "OldPassword123!",
            "new_password": "NewPassword456!",
        },
        headers={"Authorization": f"Bearer {current_access}"},
    )
    assert pw_res.status_code == 200
    assert "invalidated" in pw_res.json()["message"].lower()

    # 5. CONFIRM old access token NOW FAILS with 401
    fail_me = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {current_access}"}
    )
    assert (
        fail_me.status_code == 401
    ), "Old access token should be invalidated after password change!"

    # 6. CONFIRM old refresh token NOW FAILS with 401
    fail_ref = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": current_refresh}
    )
    assert (
        fail_ref.status_code == 401
    ), "Old refresh token should be invalidated after password change!"

    # 7. Login with NEW password and verify new token_version is 1
    new_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "versionuser@example.com",
            "password": "NewPassword456!",
        },
    )
    assert new_login.status_code == 200
    new_access = new_login.json()["access_token"]

    me_after = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {new_access}"}
    )
    assert me_after.status_code == 200
    assert me_after.json()["token_version"] == 1
