import asyncio
import io
import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

os.environ["BACKEND_DATABASE_URL"] = "sqlite+aiosqlite:///./test_rag.db"
os.environ["BACKEND_ENVIRONMENT"] = "testing"

from sqlalchemy import select

from app.core.database import AsyncSessionLocal as async_session_maker
from app.core.database import Base, engine
from app.main import app
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.rag import index_lifecycle
from app.services.storage.cloudinary_client import CloudinaryStorageClient
from app.workers.stuck_document_detector import find_and_reprocess_stuck_documents

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def setup_rag_db():
    """Setup and teardown isolated test database for RAG pipeline tests."""

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    yield
    if os.path.exists("test_rag.db"):
        try:
            os.remove("test_rag.db")
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


def test_ingestion_pipeline_end_to_end():
    """Test full RAG ingestion: upload triggers extraction, chunking, embedding, and FAISS indexing."""
    headers = get_auth_headers("raguser@example.com", "RAG User")
    file_content = (
        b"Council of Minds is an advanced agentic artificial intelligence platform. "
        b"It encapsulates user documents into high-dimensional vector spaces using sentence transformers and FAISS."
    )
    files = {"file": ("rag_test.txt", io.BytesIO(file_content), "text/plain")}

    # Upload document -> BackgroundTasks runs synchronously in Starlette TestClient
    response = client.post("/api/v1/documents", headers=headers, files=files)
    assert response.status_code == 201
    doc_id = response.json()["id"]

    # Verify status is ready
    get_res = client.get(f"/api/v1/documents/{doc_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["status"] == "ready"

    # Verify DocumentChunk rows created in DB and FAISS index search works
    async def check_index_and_db():
        async with async_session_maker() as db:
            doc_uuid = uuid.UUID(doc_id)
            stmt = select(Document).where(Document.id == doc_uuid)
            res = await db.execute(stmt)
            doc = res.scalar_one()

            stmt_chunks = select(DocumentChunk).where(
                DocumentChunk.document_id == doc_uuid
            )
            res_chunks = await db.execute(stmt_chunks)
            chunks = list(res_chunks.scalars().all())
            assert len(chunks) > 0

            storage = CloudinaryStorageClient()
            search_res = await index_lifecycle.search_user_index(
                user_id=doc.user_id,
                query_text="agentic artificial intelligence platform",
                top_k=5,
                db=db,
                storage_client=storage,
            )
            assert search_res["status"] == "success"
            assert len(search_res["results"]) > 0
            return len(chunks)

    initial_chunk_count = asyncio.run(check_index_and_db())

    # Test Idempotency & Retry Endpoint
    retry_res = client.post(f"/api/v1/documents/{doc_id}/retry", headers=headers)
    assert retry_res.status_code == 200
    assert retry_res.json()["status"] == "uploaded"

    # Verify status is ready after background task completes
    get_retry_res = client.get(f"/api/v1/documents/{doc_id}", headers=headers)
    assert get_retry_res.status_code == 200
    assert get_retry_res.json()["status"] == "ready"

    async def verify_no_duplicate_chunks():
        async with async_session_maker() as db:
            doc_uuid = uuid.UUID(doc_id)
            stmt_chunks = select(DocumentChunk).where(
                DocumentChunk.document_id == doc_uuid
            )
            res_chunks = await db.execute(stmt_chunks)
            chunks = list(res_chunks.scalars().all())
            assert len(chunks) == initial_chunk_count

    asyncio.run(verify_no_duplicate_chunks())


def test_stuck_document_detection():
    """Test that find_and_reprocess_stuck_documents identifies documents stuck in processing."""
    headers = get_auth_headers("stuckuser@example.com", "Stuck User")
    file_content = b"Stuck document test content."
    files = {"file": ("stuck.txt", io.BytesIO(file_content), "text/plain")}
    res = client.post("/api/v1/documents", headers=headers, files=files)
    doc_id = res.json()["id"]

    async def simulate_stuck_and_recover():
        async with async_session_maker() as db:
            doc_uuid = uuid.UUID(doc_id)
            stmt = select(Document).where(Document.id == doc_uuid)
            r = await db.execute(stmt)
            doc = r.scalar_one()
            # Manually force stuck processing state (> 15 min ago)
            doc.status = "processing"
            doc.updated_at = datetime.now(timezone.utc) - timedelta(minutes=20)
            await db.commit()

            # Run stuck detector
            stuck_docs = await find_and_reprocess_stuck_documents(db)
            assert len(stuck_docs) >= 1
            assert any(str(d.id) == doc_id for d in stuck_docs)

    asyncio.run(simulate_stuck_and_recover())
