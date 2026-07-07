from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.agent_response import AgentResponse


class SendMessageRequest(BaseModel):
    """Request payload for sending a question to the chat pipeline."""

    question: str = Field(..., description="The user's question or prompt.")
    chat_id: Optional[UUID] = Field(
        default=None,
        description="Optional ID of an existing chat session. If None, a new chat is created.",
    )


class MessageEvidenceResponse(BaseModel):
    """Retrieved document evidence linked to an assistant message."""

    id: UUID = Field(..., description="Unique ID of the message evidence link.")
    chunk_id: UUID = Field(
        ..., description="Unique ID of the retrieved document chunk."
    )
    similarity_score: float = Field(
        ..., description="Normalized FAISS similarity score [0, 1]."
    )
    content: str = Field(
        default="", description="The text content of the document chunk."
    )
    document_name: Optional[str] = Field(
        default=None, description="Filename of the source document."
    )

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Complete message representation including optional agent responses and evidence."""

    id: UUID = Field(..., description="Unique ID of the message.")
    chat_id: UUID = Field(..., description="ID of the chat session.")
    role: str = Field(
        ..., description="Role of the message sender ('user' or 'assistant')."
    )
    content: str = Field(..., description="Text content of the message.")
    status: str = Field(
        default="success",
        description="Status of the message ('success' or 'failed').",
    )

    # Nullable confidence breakdown fields (assistant only)
    confidence_score: Optional[float] = Field(
        default=None, description="Final confidence score (0.0 to 1.0)."
    )
    retrieval_quality: Optional[float] = Field(
        default=None, description="Retrieval quality signal score [0, 1]."
    )
    evidence_coverage: Optional[float] = Field(
        default=None, description="Evidence coverage signal score [0, 1]."
    )
    agent_agreement: Optional[float] = Field(
        default=None, description="Agent agreement signal score [0, 1]."
    )
    weights_used: Optional[Dict[str, Any]] = Field(
        default=None, description="Weights applied to confidence signals."
    )

    created_at: datetime = Field(
        ..., description="Timestamp when the message was created."
    )

    agent_responses: List[AgentResponse] = Field(
        default_factory=list,
        description="List of individual agent outputs and challenger critique (assistant only).",
    )
    evidence: List[MessageEvidenceResponse] = Field(
        default_factory=list,
        description="List of retrieved document evidence chunks linked to this reply (assistant only).",
    )

    model_config = ConfigDict(from_attributes=True)
