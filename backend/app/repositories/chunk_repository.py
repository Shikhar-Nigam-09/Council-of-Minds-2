import uuid
from typing import List

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_chunk import DocumentChunk


class ChunkRepository:
    """Repository layer for DocumentChunk CRUD and query operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_bulk(
        self,
        document_id: uuid.UUID | str,
        user_id: uuid.UUID | str,
        chunks: List[dict],
    ) -> List[DocumentChunk]:
        """Bulk create document chunks."""
        if isinstance(document_id, str):
            document_id = uuid.UUID(document_id)
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        chunk_objs = []
        for chunk in chunks:
            obj = DocumentChunk(
                id=chunk.get("id", uuid.uuid4()),
                document_id=document_id,
                user_id=user_id,
                chunk_index=chunk["chunk_index"],
                content=chunk["content"],
                faiss_vector_id=str(chunk["faiss_vector_id"]),
            )
            self.db.add(obj)
            chunk_objs.append(obj)

        await self.db.commit()
        for obj in chunk_objs:
            await self.db.refresh(obj)
        return chunk_objs

    async def delete_by_document_id(self, document_id: uuid.UUID | str) -> int:
        """Delete all chunks for a specific document (idempotency support)."""
        if isinstance(document_id, str):
            document_id = uuid.UUID(document_id)
        stmt = delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def list_by_document_id(
        self, document_id: uuid.UUID | str
    ) -> List[DocumentChunk]:
        """List chunks for a specific document ordered by chunk index."""
        if isinstance(document_id, str):
            document_id = uuid.UUID(document_id)
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_by_document_id_paginated(
        self, document_id: uuid.UUID | str, page: int = 1, page_size: int = 20
    ) -> tuple[List[DocumentChunk], int]:
        """List chunks for a specific document with pagination and total count."""
        if isinstance(document_id, str):
            document_id = uuid.UUID(document_id)
        from sqlalchemy import func

        count_stmt = (
            select(func.count())
            .select_from(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
        )
        total_res = await self.db.execute(count_stmt)
        total = total_res.scalar_one()

        offset = (page - 1) * page_size
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self.db.execute(stmt)
        chunks = list(result.scalars().all())
        return chunks, total

    async def list_by_user_id(self, user_id: uuid.UUID | str) -> List[DocumentChunk]:
        """List all chunks owned by a user (authoritative source of truth for index rebuild)."""
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.user_id == user_id)
            .order_by(DocumentChunk.created_at.asc(), DocumentChunk.chunk_index.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
