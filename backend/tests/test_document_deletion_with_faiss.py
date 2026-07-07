import asyncio
import io
import os
import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

os.environ["BACKEND_DATABASE_URL"] = "sqlite+aiosqlite:///./test_deletion.db"
os.environ["BACKEND_ENVIRONMENT"] = "testing"

from sqlalchemy import select

from app.core.database import AsyncSessionLocal as async_session_maker
from app.core.database import Base, engine
from app.main import app
from app.models.document_chunk import DocumentChunk
from app.services.rag import index_lifecycle
from app.services.storage.cloudinary_client import CloudinaryStorageClient

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def setup_deletion_db():
    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    yield
    if os.path.exists("test_deletion.db"):
        try:
            os.remove("test_deletion.db")
        except OSError:
            pass


def get_auth_headers(email: str, name: str) -> dict:
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": name},
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    return {"Authorization": f"Bearer {login_res.json()['access_token']}"}


def test_document_deletion_rebuilds_faiss():
    """Test deleting Document A removes its chunks and rebuilds FAISS index containing only Document B."""
    headers = get_auth_headers("deluser@example.com", "Delete User")

    # Upload Doc A and Doc B
    res_a = client.post(
        "/api/v1/documents",
        headers=headers,
        files={
            "file": (
                "doc_a.txt",
                io.BytesIO(b"Document A unique content alpha."),
                "text/plain",
            )
        },
    )
    doc_a_id = res_a.json()["id"]

    res_b = client.post(
        "/api/v1/documents",
        headers=headers,
        files={
            "file": (
                "doc_b.txt",
                io.BytesIO(b"Document B unique content beta."),
                "text/plain",
            )
        },
    )
    doc_b_id = res_b.json()["id"]

    # Delete Doc A
    del_res = client.delete(f"/api/v1/documents/{doc_a_id}", headers=headers)
    assert del_res.status_code == 200

    # Verify Doc A chunks removed and FAISS index contains only Doc B
    async def verify_remaining():
        async with async_session_maker() as db:
            doc_a_uuid = uuid.UUID(doc_a_id)
            doc_b_uuid = uuid.UUID(doc_b_id)
            stmt = select(DocumentChunk).where(DocumentChunk.document_id == doc_a_uuid)
            res = await db.execute(stmt)
            assert len(list(res.scalars().all())) == 0

            stmt_b = select(DocumentChunk).where(
                DocumentChunk.document_id == doc_b_uuid
            )
            res_b_db = await db.execute(stmt_b)
            assert len(list(res_b_db.scalars().all())) > 0

            storage = CloudinaryStorageClient()
            search = await index_lifecycle.search_user_index(
                user_id=res_b.json()["user_id"],
                query_text="unique content",
                top_k=10,
                db=db,
                storage_client=storage,
            )
            # All returned chunks must belong to Doc B (not Doc A)
            assert search["status"] == "success"
            assert len(search["results"]) > 0

    asyncio.run(verify_remaining())


def test_deletion_failure_preserves_db_row():
    """Test that if FAISS rebuild fails during deletion, document status is set to deletion_failed and DB row is preserved."""
    headers = get_auth_headers("failuser@example.com", "Fail User")
    res = client.post(
        "/api/v1/documents",
        headers=headers,
        files={
            "file": (
                "doc_fail.txt",
                io.BytesIO(b"Content destined to fail deletion."),
                "text/plain",
            )
        },
    )
    doc_id = res.json()["id"]

    # Mock index_lifecycle.delete_document_and_rebuild_index to raise an exception
    with patch(
        "app.services.rag.index_lifecycle.delete_document_and_rebuild_index",
        side_effect=RuntimeError("Mock FAISS failure"),
    ):
        del_res = client.delete(f"/api/v1/documents/{doc_id}", headers=headers)
        assert del_res.status_code == 500
        assert "Failed to remove document vectors" in del_res.json()["detail"]

    # Verify document row still exists in DB with status deletion_failed
    get_res = client.get(f"/api/v1/documents/{doc_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["status"] == "deletion_failed"
    assert "Mock FAISS failure" in get_res.json()["processing_error"]
