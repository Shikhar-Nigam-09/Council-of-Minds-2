import logging
import uuid
from typing import Optional, Tuple

import faiss
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.chunk_repository import ChunkRepository
from app.services.rag import vector_store
from app.services.rag.embedding_service import embedding_service
from app.services.rag.faiss_lock_registry import get_lock
from app.services.storage.storage_interface import StorageInterface

logger = logging.getLogger(__name__)


async def _get_or_recover_index(
    user_id: str | uuid.UUID,
    db: AsyncSession,
    storage_client: StorageInterface,
) -> Tuple[Optional[faiss.IndexIDMap], Optional[dict]]:
    """Internal unlocked helper: load index from cache/cloud, or recover from authoritative DB chunks."""
    index, metadata = await vector_store.load_index(user_id, storage_client)
    if index is not None and metadata is not None:
        return index, metadata

    # Check authoritative DB chunks for recovery
    repo = ChunkRepository(db)
    chunks = await repo.list_by_user_id(user_id)
    if not chunks:
        return None, None

    logger.info(
        f"Authoritative chunks found in DB (n={len(chunks)}) but FAISS index missing. Rebuilding index..."
    )
    embeddings = embedding_service.embed_texts([c.content for c in chunks])
    index, metadata = await vector_store.rebuild_index_from_chunks(
        user_id=user_id,
        chunks=chunks,
        embeddings=embeddings,
        storage_client=storage_client,
    )
    return index, metadata


async def get_or_recover_index(
    user_id: str | uuid.UUID,
    db: AsyncSession,
    storage_client: StorageInterface,
) -> Tuple[Optional[faiss.IndexIDMap], Optional[dict]]:
    """Public locked method: load index or recover from DB chunks."""
    async with get_lock(user_id):
        return await _get_or_recover_index(user_id, db, storage_client)


async def add_document_chunks_to_index(
    user_id: str | uuid.UUID,
    chunk_objs: list,
    storage_client: StorageInterface,
    db: AsyncSession,
) -> None:
    """Public locked method: embed chunks and add vectors to user's FAISS index."""
    if not chunk_objs:
        return

    async with get_lock(user_id):
        index, metadata = await _get_or_recover_index(user_id, db, storage_client)
        if index is None or metadata is None:
            index, metadata = vector_store.build_index()

        embeddings = embedding_service.embed_texts([c.content for c in chunk_objs])
        await vector_store.add_vectors(
            user_id=user_id,
            index=index,
            metadata=metadata,
            embeddings=embeddings,
            chunk_ids=[c.id for c in chunk_objs],
            storage_client=storage_client,
        )


async def _rebuild_user_index(
    user_id: str | uuid.UUID,
    db: AsyncSession,
    storage_client: StorageInterface,
    chunks: Optional[list] = None,
) -> Tuple[Optional[faiss.IndexIDMap], Optional[dict]]:
    """Internal unlocked helper: rebuild user index from all remaining DB chunks."""
    if chunks is None:
        repo = ChunkRepository(db)
        chunks = await repo.list_by_user_id(user_id)

    if not chunks or len(chunks) == 0:
        await vector_store.delete_index(user_id, storage_client)
        return None, None

    embeddings = embedding_service.embed_texts([c.content for c in chunks])
    return await vector_store.rebuild_index_from_chunks(
        user_id=user_id,
        chunks=chunks,
        embeddings=embeddings,
        storage_client=storage_client,
    )


async def rebuild_user_index(
    user_id: str | uuid.UUID,
    db: AsyncSession,
    storage_client: StorageInterface,
    chunks: Optional[list] = None,
) -> Tuple[Optional[faiss.IndexIDMap], Optional[dict]]:
    """Public locked method: rebuild user index from all remaining DB chunks."""
    async with get_lock(user_id):
        return await _rebuild_user_index(user_id, db, storage_client, chunks)


async def delete_document_and_rebuild_index(
    user_id: str | uuid.UUID,
    document_id: str | uuid.UUID,
    db: AsyncSession,
    storage_client: StorageInterface,
) -> None:
    """Public locked method: delete document chunks from DB and rebuild user index."""
    async with get_lock(user_id):
        repo = ChunkRepository(db)
        await repo.delete_by_document_id(document_id)
        await _rebuild_user_index(user_id, db, storage_client)


async def search_user_index(
    user_id: str | uuid.UUID,
    query_text: str,
    top_k: int,
    db: AsyncSession,
    storage_client: StorageInterface,
) -> dict:
    """Public locked method: search user's FAISS index."""
    async with get_lock(user_id):
        index, metadata = await _get_or_recover_index(user_id, db, storage_client)
        if index is None or index.ntotal == 0:
            return {
                "status": "no_index",
                "results": [],
                "message": "No indexed documents available for this user.",
            }
        query_vector = embedding_service.embed_query(query_text)
        return vector_store.search(user_id, index, metadata, query_vector, top_k)
