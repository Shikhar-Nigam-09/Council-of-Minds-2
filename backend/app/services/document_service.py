import logging
import os
import uuid
from typing import List, Optional

from fastapi import BackgroundTasks, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.document import Document
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.services.rag import index_lifecycle
from app.services.storage.storage_interface import StorageInterface
from app.workers.ingestion_worker import background_ingest_document

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
ALLOWED_MIMES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "text/x-markdown",
    "application/octet-stream",
}


class DocumentService:
    """Service layer for document validation, cloud storage, and database management."""

    def __init__(self, db: AsyncSession, storage_client: StorageInterface):
        self.db = db
        self.repo = DocumentRepository(db)
        self.storage = storage_client

    async def validate_file(self, file: UploadFile) -> bytes:
        """Validate file type and size before uploading."""
        filename = file.filename or "untitled.txt"
        ext = os.path.splitext(filename)[1].lower()

        if ext not in ALLOWED_EXTENSIONS and file.content_type not in ALLOWED_MIMES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type '{file.content_type}' or extension '{ext}'. Only PDF, TXT, and MD are allowed.",
            )

        content = await file.read()
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"File size ({len(content)} bytes) exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB.",
            )
        return content

    async def upload_document(
        self,
        user: User,
        file: UploadFile,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> Document:
        """Upload file to Cloudinary and persist metadata in DB with rollback handling."""
        file_bytes = await self.validate_file(file)
        filename = file.filename or "untitled.txt"
        folder = f"documents/{user.id}"

        # Step 1: Upload to Cloudinary storage
        try:
            public_id, secure_url = await self.storage.upload_file(
                file_bytes=file_bytes, filename=filename, folder=folder
            )
        except Exception as e:
            logger.error(f"Storage upload failed for user {user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to cloud storage.",
            )

        # Step 2: Persist in PostgreSQL DB within transaction; rollback Cloudinary if DB write fails
        try:
            doc = await self.repo.create(
                user_id=user.id,
                original_filename=filename,
                cloudinary_public_id=public_id,
                cloudinary_url=secure_url,
                file_type=file.content_type or "application/octet-stream",
                file_size_bytes=len(file_bytes),
                status="uploaded",
            )
            logger.info(f"Document uploaded successfully: {doc.id} ({filename})")

            # Step 3: Trigger background RAG ingestion pipeline
            if background_tasks:
                background_tasks.add_task(background_ingest_document, doc.id)
                logger.info(f"Scheduled background ingestion task for doc {doc.id}")

            return doc
        except Exception as db_err:
            logger.error(
                f"DB write failed for document {filename}: {str(db_err)}. Rolling back Cloudinary asset."
            )
            await self.storage.delete_file(public_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save document metadata.",
            )

    async def list_user_documents(self, user: User) -> List[Document]:
        """List all documents owned by the authenticated user."""
        return await self.repo.list_by_user(user.id)

    async def get_user_document(self, user: User, doc_id: str | uuid.UUID) -> Document:
        """Get a specific document owned by the authenticated user."""
        doc = await self.repo.get_by_id_for_user(doc_id, user.id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or access denied.",
            )
        return doc

    async def rename_document(
        self, user: User, doc_id: str | uuid.UUID, new_filename: str
    ) -> Document:
        """Rename original filename of a document owned by the user."""
        doc = await self.get_user_document(user, doc_id)
        return await self.repo.rename(doc, new_filename)

    async def delete_storage_and_row(self, doc: Document) -> None:
        """Delete file from Cloudinary storage and remove row from PostgreSQL DB."""
        await self.storage.delete_file(doc.cloudinary_public_id)
        await self.repo.delete(doc)

    async def delete_document(self, user: User, doc_id: str | uuid.UUID) -> None:
        """FAISS-aware two-step deletion: vector cleanup & index rebuild + storage/DB removal."""
        doc = await self.get_user_document(user, doc_id)

        # Step 1: Remove chunks from DB and rebuild FAISS index under lock
        try:
            await index_lifecycle.delete_document_and_rebuild_index(
                user_id=user.id,
                document_id=doc.id,
                db=self.db,
                storage_client=self.storage,
            )
        except Exception as e:
            logger.error(
                f"FAISS index deletion rebuild failed for doc {doc.id}: {str(e)}"
            )
            doc.status = "deletion_failed"
            doc.processing_error = (
                f"Failed to remove document vectors from FAISS index: {str(e)}"
            )
            await self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to remove document vectors from FAISS index: {str(e)}",
            )

        # Step 2: Delete original file from Cloudinary storage and remove Document row from DB
        await self.delete_storage_and_row(doc)
        logger.info(
            f"Document deleted successfully: {doc.id} ({doc.original_filename})"
        )
