import asyncio
import os
import shutil
import uuid

import numpy as np
import pytest

os.environ["BACKEND_DATABASE_URL"] = "sqlite+aiosqlite:///./test_lifecycle.db"
os.environ["BACKEND_ENVIRONMENT"] = "testing"

from app.core.database import AsyncSessionLocal as async_session_maker
from app.core.database import Base, engine
from app.models.document_chunk import DocumentChunk
from app.services.rag import index_lifecycle, vector_store
from app.services.storage.cloudinary_client import CloudinaryStorageClient


@pytest.fixture(autouse=True, scope="module")
def setup_lifecycle_db():
    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    yield
    if os.path.exists("test_lifecycle.db"):
        try:
            os.remove("test_lifecycle.db")
        except OSError:
            pass


def test_faiss_store_and_lazy_load():
    """Test saving FAISS index, deleting local disk cache, and lazy-loading back from Cloudinary."""
    user_id = uuid.uuid4()
    storage = CloudinaryStorageClient()

    async def run_test():
        index, metadata = vector_store.build_index(dimension=3)
        embeddings = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32)
        chunk_ids = [uuid.uuid4(), uuid.uuid4()]

        await vector_store.add_vectors(
            user_id, index, metadata, embeddings, chunk_ids, storage
        )
        assert index.ntotal == 2

        # Clear local cache
        cache_dir = vector_store.get_cache_dir(user_id)
        shutil.rmtree(cache_dir, ignore_errors=True)
        assert not os.path.exists(cache_dir)

        # Lazy load from Cloudinary storage
        loaded_index, loaded_meta = await vector_store.load_index(user_id, storage)
        assert loaded_index is not None
        assert loaded_index.ntotal == 2
        assert len(loaded_meta["id_to_uuid"]) == 2

    asyncio.run(run_test())


def test_authoritative_recovery_from_db():
    """Test that if FAISS index is completely missing from cache and cloud, it rebuilds from DB DocumentChunk rows."""
    user_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    storage = CloudinaryStorageClient()

    async def run_test():
        async with async_session_maker() as db:
            # Create dummy DocumentChunk rows in DB
            chunk1 = DocumentChunk(
                id=uuid.uuid4(),
                document_id=doc_id,
                user_id=user_id,
                chunk_index=0,
                content="Council of Minds knowledge chunk one.",
                faiss_vector_id="1",
            )
            chunk2 = DocumentChunk(
                id=uuid.uuid4(),
                document_id=doc_id,
                user_id=user_id,
                chunk_index=1,
                content="Council of Minds knowledge chunk two.",
                faiss_vector_id="2",
            )
            db.add_all([chunk1, chunk2])
            await db.commit()

            # Ensure no FAISS index exists anywhere
            await vector_store.delete_index(user_id, storage)

            # Call get_or_recover_index -> should detect DB chunks and rebuild FAISS index!
            index, meta = await index_lifecycle.get_or_recover_index(
                user_id, db, storage
            )
            assert index is not None
            assert index.ntotal == 2
            assert str(chunk1.id) in meta["uuid_to_id"]
            assert str(chunk2.id) in meta["uuid_to_id"]

    asyncio.run(run_test())
