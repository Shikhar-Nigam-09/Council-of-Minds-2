import asyncio
import logging
import uuid
from typing import Dict

logger = logging.getLogger(__name__)

# In-process per-user async lock registry
_locks: Dict[str, asyncio.Lock] = {}


def get_lock(user_id: str | uuid.UUID) -> asyncio.Lock:
    """Get or create an in-process asyncio.Lock for a specific user ID.

    This serializes FAISS index mutations (ingestion and deletion) for a single user
    within a single backend instance without blocking different users.
    """
    uid_str = str(user_id)
    if uid_str not in _locks:
        _locks[uid_str] = asyncio.Lock()
    return _locks[uid_str]
