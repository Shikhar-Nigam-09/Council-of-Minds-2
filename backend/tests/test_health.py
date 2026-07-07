from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test that GET /health returns 200 OK and expected JSON structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["environment"] == settings.ENVIRONMENT
    assert data["version"] == settings.VERSION
