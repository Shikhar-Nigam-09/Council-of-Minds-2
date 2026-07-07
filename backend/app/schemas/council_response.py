from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.agent_response import AgentResponse


class ChunkRef(BaseModel):
    """Reference to a retrieved context chunk used in the council evaluation."""

    chunk_id: Optional[UUID | str] = Field(
        default=None, description="Optional UUID or identifier of the document chunk."
    )
    content: str = Field(..., description="The textual content of the retrieved chunk.")
    similarity_score: float = Field(
        default=0.0, description="Normalized FAISS similarity score [0, 1]."
    )
    document_name: Optional[str] = Field(
        default=None, description="Filename of the source document."
    )

    model_config = ConfigDict(from_attributes=True)


class ConfidenceBreakdown(BaseModel):
    """
    Explainable breakdown of the System-Estimated Confidence Score.

    Note: This is explicitly NOT a probability of correctness. It is a deterministic,
    reproducible score derived from three normalized signals: retrieval quality,
    evidence coverage, and inter-agent agreement.
    """

    final_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Weighted final confidence score (0.0 to 1.0). Presented as 0-100 on frontend.",
    )
    retrieval_quality: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized FAISS similarity of retrieved chunks [0, 1].",
    )
    evidence_coverage: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Semantic evidence support proportion traceable to retrieved chunks [0, 1].",
    )
    agent_agreement: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Pairwise perspective convergence across successful agent answers [0, 1].",
    )
    weights_used: Dict[str, float] = Field(
        ...,
        description="The exact weights applied to each signal during calculation.",
    )

    model_config = ConfigDict(from_attributes=True)


class ChallengeCritique(BaseModel):
    """Structured critique produced by the Challenger agent."""

    critique_summary: str = Field(
        default="", description="Overall summary of the critique."
    )
    weaknesses: List[str] = Field(
        default_factory=list, description="Identified logical or empirical weaknesses."
    )
    unsupported_claims: List[str] = Field(
        default_factory=list,
        description="Claims in the answer not supported by retrieved context.",
    )
    missing_considerations: List[str] = Field(
        default_factory=list,
        description="Important edge cases or considerations overlooked.",
    )

    model_config = ConfigDict(from_attributes=True)


class CouncilResponse(BaseModel):
    """Complete response from the Council of Minds evaluation pipeline."""

    final_answer: str = Field(
        ..., description="The synthesized answer from the Aggregator agent."
    )
    challenge_critique: ChallengeCritique = Field(
        ..., description="The critique from the Challenger agent."
    )
    confidence: ConfidenceBreakdown = Field(
        ...,
        description="The explainable System-Estimated Confidence Score and breakdown.",
    )
    agent_responses: List[AgentResponse] = Field(
        ..., description="Individual outputs from the five reasoning personas."
    )
    retrieved_chunks: List[ChunkRef] = Field(
        ..., description="The context chunks retrieved and evaluated by the council."
    )

    model_config = ConfigDict(from_attributes=True)
