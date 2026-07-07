import asyncio
import io
import os

import pytest
from fastapi.testclient import TestClient

os.environ["BACKEND_DATABASE_URL"] = "sqlite+aiosqlite:///./test_docs.db"
os.environ["BACKEND_ENVIRONMENT"] = "testing"

from app.core.database import Base, engine
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def setup_docs_db():
    """Setup and teardown isolated test database for document management tests."""

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    yield
    if os.path.exists("test_docs.db"):
        try:
            os.remove("test_docs.db")
        except OSError:
            pass


def get_auth_headers(email: str, name: str) -> dict:
    """Helper to register/login a user and return Bearer auth headers."""
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": name},
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_document_success():
    """Test successful upload of TXT document by User A."""
    headers = get_auth_headers("usera@example.com", "User A")
    file_content = b"This is a valid test text document for Council of Minds."
    files = {"file": ("test_doc.txt", io.BytesIO(file_content), "text/plain")}

    response = client.post("/api/v1/documents", headers=headers, files=files)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["original_filename"] == "test_doc.txt"
    assert data["status"] == "uploaded"
    assert data["file_size_bytes"] == len(file_content)
    assert "cloudinary.com" in data["cloudinary_url"]


def test_upload_disallowed_file_type():
    """Test uploading an unsupported file type (.exe or image/png) returns 400."""
    headers = get_auth_headers("usera@example.com", "User A")
    files = {
        "file": (
            "malicious.exe",
            io.BytesIO(b"fake exe content"),
            "application/x-msdownload",
        )
    }

    response = client.post("/api/v1/documents", headers=headers, files=files)
    assert response.status_code == 400
    assert "unsupported file type" in response.json()["detail"].lower()


def test_upload_oversized_file():
    """Test uploading a file larger than MAX_UPLOAD_SIZE_MB returns 413."""
    headers = get_auth_headers("usera@example.com", "User A")
    # MAX_UPLOAD_SIZE_MB defaults to 10 MB in config; create 11 MB dummy content
    oversized_content = b"0" * (11 * 1024 * 1024)
    files = {"file": ("huge_doc.txt", io.BytesIO(oversized_content), "text/plain")}

    response = client.post("/api/v1/documents", headers=headers, files=files)
    assert response.status_code == 413
    assert "exceeds maximum allowed size" in response.json()["detail"].lower()


def test_list_and_get_user_documents():
    """Test listing documents and fetching specific details scoped to owner."""
    headers = get_auth_headers("usera@example.com", "User A")
    list_res = client.get("/api/v1/documents", headers=headers)
    assert list_res.status_code == 200
    docs = list_res.json()
    assert len(docs) >= 1
    doc_id = docs[0]["id"]

    get_res = client.get(f"/api/v1/documents/{doc_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == doc_id


def test_user_isolation_cannot_access_other_user_doc():
    """Test that User B cannot view or delete User A's document."""
    headers_a = get_auth_headers("usera@example.com", "User A")
    list_res = client.get("/api/v1/documents", headers=headers_a)
    doc_id = list_res.json()[0]["id"]

    headers_b = get_auth_headers("userb@example.com", "User B")

    # User B tries to get User A's doc -> 404
    get_res = client.get(f"/api/v1/documents/{doc_id}", headers=headers_b)
    assert get_res.status_code == 404

    # User B tries to delete User A's doc -> 404
    del_res = client.delete(f"/api/v1/documents/{doc_id}", headers=headers_b)
    assert del_res.status_code == 404


def test_rename_document():
    """Test renaming a document filename."""
    headers = get_auth_headers("usera@example.com", "User A")
    list_res = client.get("/api/v1/documents", headers=headers)
    doc_id = list_res.json()[0]["id"]

    rename_res = client.patch(
        f"/api/v1/documents/{doc_id}",
        headers=headers,
        json={"new_filename": "renamed_doc.txt"},
    )
    assert rename_res.status_code == 200
    assert rename_res.json()["original_filename"] == "renamed_doc.txt"


def test_delete_document_success():
    """Test owner successfully deleting their document."""
    headers = get_auth_headers("usera@example.com", "User A")
    list_res = client.get("/api/v1/documents", headers=headers)
    doc_id = list_res.json()[0]["id"]

    del_res = client.delete(f"/api/v1/documents/{doc_id}", headers=headers)
    assert del_res.status_code == 200
    assert "deleted successfully" in del_res.json()["message"].lower()

    # Confirm row is removed
    get_res = client.get(f"/api/v1/documents/{doc_id}", headers=headers)
    assert get_res.status_code == 404
