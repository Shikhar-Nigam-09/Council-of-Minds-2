import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_valid_confidence_weights(monkeypatch):
    """Test that valid weights summing to 1.0 pass validation cleanly."""
    monkeypatch.setenv("BACKEND_CONFIDENCE_WEIGHT_RETRIEVAL", "0.40")
    monkeypatch.setenv("BACKEND_CONFIDENCE_WEIGHT_EVIDENCE", "0.40")
    monkeypatch.setenv("BACKEND_CONFIDENCE_WEIGHT_AGREEMENT", "0.20")

    settings = Settings()
    assert settings.CONFIDENCE_WEIGHT_RETRIEVAL == 0.40
    assert settings.CONFIDENCE_WEIGHT_EVIDENCE == 0.40
    assert settings.CONFIDENCE_WEIGHT_AGREEMENT == 0.20


def test_invalid_sum_confidence_weights(monkeypatch):
    """Test that weights summing to > 1.0 or < 1.0 fail fast with ValueError/ValidationError."""
    monkeypatch.setenv("BACKEND_CONFIDENCE_WEIGHT_RETRIEVAL", "0.50")
    monkeypatch.setenv("BACKEND_CONFIDENCE_WEIGHT_EVIDENCE", "0.50")
    monkeypatch.setenv("BACKEND_CONFIDENCE_WEIGHT_AGREEMENT", "0.50")

    with pytest.raises((ValueError, ValidationError)) as exc_info:
        Settings()
    assert "must sum to 1.0" in str(exc_info.value)


def test_negative_confidence_weights(monkeypatch):
    """Test that negative weights fail fast with ValueError/ValidationError."""
    monkeypatch.setenv("BACKEND_CONFIDENCE_WEIGHT_RETRIEVAL", "-0.10")
    monkeypatch.setenv("BACKEND_CONFIDENCE_WEIGHT_EVIDENCE", "0.60")
    monkeypatch.setenv("BACKEND_CONFIDENCE_WEIGHT_AGREEMENT", "0.50")

    with pytest.raises((ValueError, ValidationError)) as exc_info:
        Settings()
    assert "must be non-negative" in str(exc_info.value)
