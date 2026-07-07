import asyncio
import os
import uuid

import pytest
from fastapi.testclient import TestClient

os.environ["BACKEND_DATABASE_URL"] = "sqlite+aiosqlite:///./test_hardening.db"
os.environ["BACKEND_ENVIRONMENT"] = "testing"

from app.core.database import Base, engine
from app.core.exceptions import (
    ExternalServiceError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from app.core.rate_limiter import limiter
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def setup_test_db():
    """Setup and teardown isolated test database for hardening tests."""

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    yield


def test_correlation_id_generation_and_propagation():
    """Verify X-Request-ID is generated when missing and propagated when provided."""
    # Case 1: Missing X-Request-ID
    res1 = client.get("/health")
    assert res1.status_code == 200
    assert "X-Request-ID" in res1.headers
    req_id1 = res1.headers["X-Request-ID"]
    assert len(req_id1) > 0 and req_id1 != "-"

    # Case 2: Provided X-Request-ID
    custom_id = "test-trace-id-999"
    res2 = client.get("/health", headers={"X-Request-ID": custom_id})
    assert res2.status_code == 200
    assert res2.headers.get("X-Request-ID") == custom_id


def test_standardized_error_envelope_404():
    """Verify 404 Not Found returns the standardized JSON error envelope."""
    fake_id = str(uuid.uuid4())
    # Requesting a non-existent document without auth returns 401, so let's check a non-existent route or document
    res = client.get(f"/api/v1/nonexistent_route_test/{fake_id}")
    assert res.status_code == 404
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "message" in data["error"]
    assert "detail" in data


def test_standardized_error_envelope_401():
    """Verify 401 Unauthorized returns the standardized JSON error envelope."""
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "UNAUTHORIZED"
    assert "detail" in data


def test_standardized_error_envelope_422():
    """Verify 422 Validation Error returns the standardized JSON error envelope with field details."""
    payload = {"email": "not-an-email", "password": "123"}
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 422
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(data["error"]["details"], list)
    assert "detail" in data


def test_rate_limiting_throttling():
    """Verify slowapi rate limiter throttles excessive requests and returns 429 error envelope."""
    limiter.enabled = True
    limiter.reset()
    endpoint = "/api/v1/auth/login"
    payload = {"email": "ratelimit@example.com", "password": "Password123!"}

    # RATE_LIMIT_AUTH_PER_MINUTE is set to "10/minute" by default
    # We send 10 requests which should not be rate limited (they return 401 due to invalid user)
    for _ in range(10):
        res = client.post(endpoint, json=payload)
        assert res.status_code in [200, 401]

    # The 11th request should exceed the limit and return 429
    res_throttled = client.post(endpoint, json=payload)
    assert res_throttled.status_code == 429
    data = res_throttled.json()
    assert "error" in data
    assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert "Rate limit exceeded" in data["error"]["message"]

    # Clean up limiter for subsequent tests
    limiter.reset()
    limiter.enabled = False


def test_custom_exceptions_instantiation():
    """Verify custom exception hierarchy attributes and defaults."""
    e404 = NotFoundError("Doc missing", details={"doc_id": "123"})
    assert e404.status_code == 404
    assert e404.code == "NOT_FOUND"
    assert e404.details == {"doc_id": "123"}

    e401 = UnauthorizedError("Token expired")
    assert e401.status_code == 401
    assert e401.code == "UNAUTHORIZED"

    e403 = ForbiddenError("Not owner")
    assert e403.status_code == 403
    assert e403.code == "FORBIDDEN"

    e422 = ValidationError("Invalid format")
    assert e422.status_code == 422
    assert e422.code == "VALIDATION_ERROR"

    e502 = ExternalServiceError("Groq API timeout")
    assert e502.status_code == 502
    assert e502.code == "EXTERNAL_SERVICE_ERROR"
