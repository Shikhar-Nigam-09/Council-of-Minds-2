import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.user import utc_now

if TYPE_CHECKING:
    from app.models.document_chunk import DocumentChunk
    from app.models.message import Message


class MessageEvidence(Base):
    """Normalized join table linking retrieved document chunks to assistant messages."""

    __tablename__ = "message_evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    message_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("document_chunks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    message: Mapped["Message"] = relationship("Message", back_populates="evidence")
    chunk: Mapped["DocumentChunk"] = relationship("DocumentChunk")

    @property
    def content(self) -> str:
        """Return the text content of the linked document chunk."""
        return self.chunk.content if self.chunk else ""

    @property
    def document_name(self) -> str | None:
        """Return the original filename of the linked document chunk."""
        return (
            self.chunk.document.original_filename
            if self.chunk and self.chunk.document
            else None
        )
