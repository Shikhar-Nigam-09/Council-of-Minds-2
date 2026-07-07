import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.user import utc_now

if TYPE_CHECKING:
    from app.models.agent_response import AgentResponse
    from app.models.chat import Chat
    from app.models.message_evidence import MessageEvidence


class Message(Base):
    """Message domain model storing individual user or assistant turns and confidence breakdowns."""

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    chat_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "user" or "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default="success", nullable=False
    )  # "success" or "failed"

    # Nullable assistant-only confidence breakdown fields
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    retrieval_quality: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    evidence_coverage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    agent_agreement: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weights_used: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
    agent_responses: Mapped[List["AgentResponse"]] = relationship(
        "AgentResponse",
        back_populates="message",
        cascade="all, delete-orphan",
    )
    evidence: Mapped[List["MessageEvidence"]] = relationship(
        "MessageEvidence",
        back_populates="message",
        cascade="all, delete-orphan",
    )
