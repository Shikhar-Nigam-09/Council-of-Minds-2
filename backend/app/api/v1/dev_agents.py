from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.schemas.council_response import ChunkRef, CouncilResponse
from app.services.council_pipeline import run_council

router = APIRouter()


class DevAgentTestRequest(BaseModel):
    """Request schema for dev-only council test endpoint."""

    question: str = Field(
        ...,
        description="Question or prompt to evaluate across all 5 personas and council.",
    )
    context_chunks: List[str] = Field(
        default_factory=list,
        description="Explicit context chunk strings to pass to the council for isolated testing.",
    )
    document_id: Optional[UUID] = Field(
        default=None,
        description="Optional Document UUID reference.",
    )
    agent_weights: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optional custom agent weights to test emphasis.",
    )
    test_empty_retrieval: bool = Field(
        default=False,
        description="Set to True to explicitly simulate an empty retrieval scenario (0 chunks).",
    )
    conversation_history: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional conversation history (accepted for forward compatibility).",
    )


def check_not_production():
    """Dependency ensuring dev endpoints are inaccessible in production environments."""
    if settings.ENVIRONMENT.lower() in ["production", "prod"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dev endpoint is disabled in production environments.",
        )


@router.post(
    "/test",
    response_model=CouncilResponse,
    summary="Dev-only test endpoint for Council of Minds pipeline",
    dependencies=[Depends(check_not_production)],
)
async def test_reasoning_agents(request: DevAgentTestRequest):
    """
    Invokes the full Council of Minds evaluation pipeline (5 reasoning personas ->
    Aggregator -> Challenger -> Confidence Engine) against the provided question and context.

    This endpoint is intended strictly for development and testing of agent personas,
    aggregator synthesis, challenger critique, and confidence scoring. It is automatically
    disabled when ENVIRONMENT=production.
    """
    chunk_refs: List[ChunkRef] = []

    if request.test_empty_retrieval:
        chunk_refs = []
    elif request.context_chunks:
        chunk_refs = [
            ChunkRef(content=c, similarity_score=0.85) for c in request.context_chunks
        ]
    elif request.document_id:
        chunk_refs = [
            ChunkRef(
                content=f"[Dev Note]: Testing with Document ID '{request.document_id}', but explicit context chunks were empty. In Phase 7, FAISS retrieval will populate these automatically.",
                similarity_score=0.80,
            )
        ]
    else:
        chunk_refs = [
            ChunkRef(
                content="Sample context chunk 1: Council of Minds is an advanced agentic RAG system.",
                similarity_score=0.88,
            ),
            ChunkRef(
                content="Sample context chunk 2: Five personas evaluate information: Logical, Rational, Practical, Spiritual, and Skeptical.",
                similarity_score=0.82,
            ),
        ]

    # Create a simple mock user settings object if weights were passed
    user_settings = None
    if request.agent_weights:
        user_settings = {"agent_weights": request.agent_weights}

    result = await run_council(
        question=request.question,
        context_chunks=chunk_refs,
        user_settings=user_settings,
        conversation_history=request.conversation_history,
    )

    return result
