import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


class DocumentRepository:
    """Repository layer for Document database queries and operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> Document:
        """Create a new document metadata record."""
        doc = Document(**kwargs)
        self.session.add(doc)
        await self.session.commit()
        await self.session.refresh(doc)
        return doc

    async def list_by_user(self, user_id: uuid.UUID | str) -> List[Document]:
        """List all documents owned by user ordered by creation date."""
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        stmt = (
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id_for_user(
        self, doc_id: uuid.UUID | str, user_id: uuid.UUID | str
    ) -> Optional[Document]:
        """Get a document by ID scoped to the owner."""
        if isinstance(doc_id, str):
            doc_id = uuid.UUID(doc_id)
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        stmt = select(Document).where(
            Document.id == doc_id, Document.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, doc_id: uuid.UUID | str) -> Optional[Document]:
        """Get a document by ID."""
        if isinstance(doc_id, str):
            doc_id = uuid.UUID(doc_id)
        stmt = select(Document).where(Document.id == doc_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, doc: Document) -> None:
        """Delete a document record from database."""
        await self.session.delete(doc)
        await self.session.commit()

    async def rename(self, doc: Document, new_filename: str) -> Document:
        """Rename document original filename."""
        doc.original_filename = new_filename
        self.session.add(doc)
        await self.session.commit()
        await self.session.refresh(doc)
        return doc
