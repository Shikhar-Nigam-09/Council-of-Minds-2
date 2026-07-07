import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.document import Document
from app.workers.ingestion_worker import background_ingest_document

logger = logging.getLogger(__name__)


async def find_and_reprocess_stuck_documents(
    db: AsyncSession, background_tasks: Optional[BackgroundTasks] = None
) -> List[Document]:
    """Find documents stuck in 'processing' beyond threshold and flag/reprocess them."""
    now = datetime.now(timezone.utc)
    threshold = now - timedelta(minutes=settings.INGESTION_STUCK_THRESHOLD_MINUTES)
    stmt = select(Document).where(Document.status == "processing")
    result = await db.execute(stmt)
    all_processing_docs = list(result.scalars().all())

    stuck_docs = []
    for doc in all_processing_docs:
        doc_updated = (
            doc.updated_at
            if doc.updated_at.tzinfo
            else doc.updated_at.replace(tzinfo=timezone.utc)
        )
        if doc_updated < threshold:
            stuck_docs.append(doc)

    if not stuck_docs:
        return []

    logger.warning(
        f"Found {len(stuck_docs)} stuck documents exceeding {settings.INGESTION_STUCK_THRESHOLD_MINUTES} min threshold."
    )
    for doc in stuck_docs:
        logger.info(f"Flagging stuck document {doc.id} ({doc.original_filename})")
        if background_tasks:
            background_tasks.add_task(background_ingest_document, doc.id)

    return stuck_docs
