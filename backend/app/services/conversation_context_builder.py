import logging
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.message_repository import MessageRepository

logger = logging.getLogger(__name__)


async def build_history(
    db: AsyncSession,
    chat_id: Optional[uuid.UUID | str],
    limit: int = settings.MAX_CHAT_HISTORY_MESSAGES,
) -> List[Dict[str, Any]]:
    """
    Fetches the most recent messages for a chat (oldest-first order once retrieved)
    and formats them into the structure expected by the council pipeline.

    Returns an empty list for a new chat or when chat_id is None.
    """
    if not chat_id:
        return []

    try:
        repo = MessageRepository(db)
        messages = await repo.list_recent_by_chat_id(chat_id=chat_id, limit=limit)

        history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
            if msg.content and msg.content.strip()
        ]
        logger.debug(
            f"Built conversation history for chat {chat_id}: {len(history)} turns retrieved (limit={limit})."
        )
        return history
    except Exception as exc:
        logger.error(
            f"Failed to build conversation history for chat {chat_id}: {exc}",
            exc_info=True,
        )
        return []
