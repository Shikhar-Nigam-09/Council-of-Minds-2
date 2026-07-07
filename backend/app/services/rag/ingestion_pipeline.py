import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.document import Document
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.rag import index_lifecycle
from app.services.rag.chunker import chunk_text
from app.services.rag.text_extractor import extract_text
from app.services.storage.storage_interface import StorageInterface

logger = logging.getLogger(__name__)


async def run_pipeline(
    document_id: str | uuid.UUID,
    db: AsyncSession,
    storage_client: StorageInterface,
    force: bool = False,
) -> Document:
    """Idempotent background RAG ingestion pipeline: extract -> chunk -> embed -> index."""
    doc_repo = DocumentRepository(db)
    chunk_repo = ChunkRepository(db)

    doc = await doc_repo.get_by_id(document_id)
    if not doc:
        logger.error(f"Ingestion pipeline aborted: Document {document_id} not found.")
        return None

    # Step 1: Check idempotency & stuck status
    if doc.status == "ready" and not force:
        logger.info(f"Document {document_id} is already processed and ready. No-op.")
        return doc

    if doc.status == "processing" and not force:
        now = datetime.now(timezone.utc)
        # Ensure updated_at is timezone-aware
        doc_updated = (
            doc.updated_at
            if doc.updated_at.tzinfo
            else doc.updated_at.replace(tzinfo=timezone.utc)
        )
        stuck_threshold = now - timedelta(
            minutes=settings.INGESTION_STUCK_THRESHOLD_MINUTES
        )
        if doc_updated > stuck_threshold:
            logger.info(
                f"Document {document_id} is currently processing (not stuck). Skipping duplicate run."
            )
            return doc
        else:
            logger.warning(
                f"Document {document_id} was stuck in processing since {doc_updated}. Reprocessing..."
            )

    # Set status to processing
    doc.status = "processing"
    doc.processing_error = None
    await db.commit()
    await db.refresh(doc)

    try:
        # Step 2: Clear pre-existing chunks for idempotency
        removed_count = await chunk_repo.delete_by_document_id(doc.id)
        if removed_count > 0:
            logger.debug(
                f"Removed {removed_count} existing chunks for doc {doc.id} before reprocessing."
            )

        # Step 3: Download file bytes from Cloudinary storage
        logger.info(
            f"Downloading file {doc.original_filename} from Cloudinary ({doc.cloudinary_url})..."
        )
        file_bytes = await storage_client.get_file_bytes(doc.cloudinary_url)

        # Step 4: Extract text
        logger.info(f"Extracting text from {doc.original_filename}...")
        text = extract_text(file_bytes, doc.file_type, doc.original_filename)

        # Step 5: Chunk text
        logger.info("Splitting text into chunks...")
        chunk_strings = chunk_text(text)
        if not chunk_strings:
            raise RuntimeError("No text chunks generated from document content.")

        # Step 6: Create DocumentChunk rows in PostgreSQL
        logger.info(f"Persisting {len(chunk_strings)} chunks to database...")
        chunk_dicts = []
        for idx, content in enumerate(chunk_strings):
            cid = uuid.uuid4()
            chunk_dicts.append(
                {
                    "id": cid,
                    "chunk_index": idx,
                    "content": content,
                    "faiss_vector_id": str(cid),
                }
            )
        chunk_objs = await chunk_repo.create_bulk(doc.id, doc.user_id, chunk_dicts)

        # Step 7: Add embeddings & vectors to FAISS index under lock
        logger.info(
            f"Embedding and indexing {len(chunk_objs)} chunks into FAISS for user {doc.user_id}..."
        )
        await index_lifecycle.add_document_chunks_to_index(
            doc.user_id, chunk_objs, storage_client, db
        )

        # Step 8: Mark document ready
        doc.status = "ready"
        doc.processing_error = None
        await db.commit()
        await db.refresh(doc)
        logger.info(
            f"Successfully completed RAG ingestion pipeline for document {doc.id}!"
        )
        return doc

    except Exception as e:
        logger.error(
            f"Ingestion pipeline failed for document {doc.id}: {str(e)}", exc_info=True
        )
        doc.status = "failed"
        doc.processing_error = str(e)
        await db.commit()
        await db.refresh(doc)
        return doc
