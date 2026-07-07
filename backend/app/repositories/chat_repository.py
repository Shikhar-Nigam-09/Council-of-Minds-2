import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import Chat
from app.models.document_chunk import DocumentChunk
from app.models.message import Message
from app.models.message_evidence import MessageEvidence


class ChatRepository:
    """Repository layer for Chat database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: uuid.UUID | str, title: str) -> Chat:
        """Create a new chat session."""
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        chat = Chat(user_id=user_id, title=title)
        self.session.add(chat)
        await self.session.commit()
        await self.session.refresh(chat)
        return chat

    async def list_by_user(self, user_id: uuid.UUID | str) -> List[Chat]:
        """List all chats owned by user ordered by last updated date."""
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        stmt = (
            select(Chat).where(Chat.user_id == user_id).order_by(Chat.updated_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id_for_user(
        self, chat_id: uuid.UUID | str, user_id: uuid.UUID | str
    ) -> Optional[Chat]:
        """Get a chat by ID scoped to the owner without loading all messages."""
        if isinstance(chat_id, str):
            chat_id = uuid.UUID(chat_id)
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        stmt = select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_detail_by_id_for_user(
        self, chat_id: uuid.UUID | str, user_id: uuid.UUID | str
    ) -> Optional[Chat]:
        """Get a chat by ID scoped to owner with eager loading of messages, responses, and evidence."""
        if isinstance(chat_id, str):
            chat_id = uuid.UUID(chat_id)
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        stmt = (
            select(Chat)
            .where(Chat.id == chat_id, Chat.user_id == user_id)
            .options(
                selectinload(Chat.messages).selectinload(Message.agent_responses),
                selectinload(Chat.messages)
                .selectinload(Message.evidence)
                .joinedload(MessageEvidence.chunk)
                .joinedload(DocumentChunk.document),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, chat: Chat) -> None:
        """Delete a chat session (cascades to messages, agent responses, and evidence)."""
        await self.session.delete(chat)
        await self.session.commit()
