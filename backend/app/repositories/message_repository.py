import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.document_chunk import DocumentChunk
from app.models.message import Message
from app.models.message_evidence import MessageEvidence


class MessageRepository:
    """Repository layer for Message database queries and operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        chat_id: uuid.UUID | str,
        role: str,
        content: str,
        status: str = "success",
        confidence_score: Optional[float] = None,
        retrieval_quality: Optional[float] = None,
        evidence_coverage: Optional[float] = None,
        agent_agreement: Optional[float] = None,
        weights_used: Optional[Dict[str, Any]] = None,
        commit: bool = True,
    ) -> Message:
        """Create a new message record."""
        if isinstance(chat_id, str):
            chat_id = uuid.UUID(chat_id)
        msg = Message(
            chat_id=chat_id,
            role=role,
            content=content,
            status=status,
            confidence_score=confidence_score,
            retrieval_quality=retrieval_quality,
            evidence_coverage=evidence_coverage,
            agent_agreement=agent_agreement,
            weights_used=weights_used,
        )
        self.session.add(msg)
        if commit:
            await self.session.commit()
            await self.session.refresh(msg)
        else:
            await self.session.flush()
        return msg

    async def update_status(
        self, message: Message, status: str, commit: bool = True
    ) -> Message:
        """Update message status (e.g., mark as failed)."""
        message.status = status
        if commit:
            await self.session.commit()
            await self.session.refresh(message)
        else:
            await self.session.flush()
        return message

    async def list_recent_by_chat_id(
        self, chat_id: uuid.UUID | str, limit: int = 10
    ) -> List[Message]:
        """Fetch the most recent messages for a chat, returned in oldest-first chronological order."""
        if isinstance(chat_id, str):
            chat_id = uuid.UUID(chat_id)
        stmt = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        messages = list(result.scalars().all())
        # Reverse to oldest-first order
        messages.reverse()
        return messages

    async def get_by_id_with_details(
        self, message_id: uuid.UUID | str
    ) -> Optional[Message]:
        """Fetch a single message with agent responses and evidence eager-loaded."""
        if isinstance(message_id, str):
            message_id = uuid.UUID(message_id)
        stmt = (
            select(Message)
            .where(Message.id == message_id)
            .options(
                selectinload(Message.agent_responses),
                selectinload(Message.evidence)
                .joinedload(MessageEvidence.chunk)
                .joinedload(DocumentChunk.document),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
