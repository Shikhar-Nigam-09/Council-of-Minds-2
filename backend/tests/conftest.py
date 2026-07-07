import os

import pytest

os.environ["BACKEND_ENVIRONMENT"] = "testing"
os.environ["BACKEND_DATABASE_URL"] = "sqlite+aiosqlite:///./test_council.db"

from app.core.rate_limiter import limiter


@pytest.fixture(autouse=True)
def reset_and_disable_rate_limiter():
    """Reset and disable slowapi rate limiter before and after each test case."""
    limiter.reset()
    limiter.enabled = False
    yield
    limiter.reset()
    limiter.enabled = False
