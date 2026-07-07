import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict

from sqlalchemy import JSON, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.user import utc_now

if TYPE_CHECKING:
    from app.models.user import User


def default_agent_weights() -> Dict[str, Any]:
    """Sensible default agent weights for Council of Minds aggregator."""
    return {
        "logical": 1.0,
        "rational": 1.0,
        "practical": 1.0,
        "spiritual": 1.0,
        "skeptical": 1.0,
    }


def default_model_settings() -> Dict[str, Any]:
    """Sensible default LLM settings for user sessions."""
    return {
        "model": "gemini-3.1-pro-high",
        "temperature": 0.7,
        "max_tokens": 4096,
    }


class UserSettings(Base):
    """UserSettings domain model storing agent weights and model preferences."""

    __tablename__ = "user_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    agent_weights: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=default_agent_weights, nullable=False
    )
    preferred_model_settings: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=default_model_settings, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="settings")
