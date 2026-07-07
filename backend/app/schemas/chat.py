from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.message import MessageResponse


class ChatSummary(BaseModel):
    """Summary view of a chat session for listing."""

    id: UUID = Field(..., description="Unique ID of the chat session.")
    title: str = Field(..., description="Title of the chat session.")
    created_at: datetime = Field(
        ..., description="Timestamp when the chat was created."
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the chat was last updated."
    )

    model_config = ConfigDict(from_attributes=True)


class ChatDetail(ChatSummary):
    """Detailed view of a chat session including all chronological messages and evaluations."""

    messages: List[MessageResponse] = Field(
        default_factory=list,
        description="Chronological list of messages in the chat session.",
    )
