import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, List

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.user import utc_now

if TYPE_CHECKING:
    from app.models.message import Message


class AgentResponse(Base):
    """
    Domain model representing an individual reasoning persona's output or challenger critique
    persisted against an assistant message.
    """

    __tablename__ = "agent_responses"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    message_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # e.g., "logical", "challenger"
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    key_points: Mapped[List[Any]] = mapped_column(JSON, nullable=False)
    self_reported_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    message: Mapped["Message"] = relationship(
        "Message", back_populates="agent_responses"
    )
