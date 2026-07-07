import logging
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings

logger = logging.getLogger(__name__)


def chunk_text(text: str) -> List[str]:
    """Split text into chunks using RecursiveCharacterTextSplitter."""
    if not text or not text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_text(text)
    logger.debug(
        f"Split text of length {len(text)} into {len(chunks)} chunks (size={settings.CHUNK_SIZE}, overlap={settings.CHUNK_OVERLAP})."
    )
    return chunks
