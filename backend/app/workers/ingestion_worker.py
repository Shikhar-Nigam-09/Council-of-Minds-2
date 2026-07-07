import logging
import uuid

from app.core.database import AsyncSessionLocal as async_session_maker
from app.services.rag.ingestion_pipeline import run_pipeline
from app.services.storage.cloudinary_client import CloudinaryStorageClient

logger = logging.getLogger(__name__)


async def background_ingest_document(document_id: str | uuid.UUID, force: bool = False):
    """Background task wrapper for running the asynchronous RAG ingestion pipeline."""
    logger.info(f"Starting background ingestion task for document {document_id}")
    async with async_session_maker() as db:
        storage_client = CloudinaryStorageClient()
        try:
            await run_pipeline(
                document_id=document_id,
                db=db,
                storage_client=storage_client,
                force=force,
            )
        except Exception as e:
            logger.error(
                f"Unhandled exception in background ingestion for doc {document_id}: {str(e)}",
                exc_info=True,
            )
