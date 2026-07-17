import logging
from typing import Any, Dict, List, Optional

from app.schemas.council_response import ChunkRef, CouncilResponse
from app.services.agents import (
    agent_orchestrator,
    aggregator_agent,
    challenger_agent,
)
from app.services.confidence.confidence_engine import confidence_engine

logger = logging.getLogger(__name__)


async def run_council(
    question: str,
    context_chunks: List[ChunkRef],
    user_settings: Optional[Any] = None,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
) -> CouncilResponse:
    """
    Orchestrates the complete Council of Minds evaluation pipeline.

    Decoupling & Contract:
    This function is completely independent of FAISS, PostgreSQL, Cloudinary, and document retrieval.
    It accepts an already-retrieved list of ChunkRef objects.

    Workflow:
    1. Extract plain text strings from ChunkRef.content for the reasoning personas and challenger.
    2. Check if retrieval is empty (len(context_chunks) == 0).
    3. Run the five specialized reasoning personas concurrently via agent_orchestrator.
    4. Extract configured agent_weights from user_settings (or fallback to defaults).
    5. Synthesize successful persona outputs via aggregator_agent.aggregate().
    6. Critique the synthesized answer via challenger_agent.critique().
    7. Compute the explainable System-Estimated Confidence Score via confidence_engine.score().
    8. Return the complete, auditable CouncilResponse.
    """
    logger.info(
        f"Starting Council evaluation for question: '{question[:60]}...' with {len(context_chunks)} chunks."
    )

    is_empty_retrieval = len(context_chunks) == 0

    # Convert ChunkRef.content to plain strings only when passing context to Phase 5 agents and Challenger
    chunk_strings = [
        chunk.content
        for chunk in context_chunks
        if chunk.content and chunk.content.strip()
    ]

    # 1. Run 5 reasoning personas in parallel
    agent_responses = await agent_orchestrator.run_agents(
        question=question,
        context_chunks=chunk_strings,
        conversation_history=conversation_history,
    )

    # Extract weights from user_settings if available
    weights = None
    if user_settings is not None:
        if hasattr(user_settings, "agent_weights"):
            weights = getattr(user_settings, "agent_weights")
        elif isinstance(user_settings, dict):
            weights = user_settings.get("agent_weights")

    # 2. Synthesize via Aggregator
    final_answer = await aggregator_agent.aggregate(
        question=question,
        agent_responses=agent_responses,
        agent_weights=weights,
        is_empty_retrieval=is_empty_retrieval,
        conversation_history=conversation_history,
    )

    # 3. Critique via Challenger
    challenge_critique = await challenger_agent.critique(
        question=question,
        aggregated_answer=final_answer,
        context_chunks=chunk_strings,
        is_empty_retrieval=is_empty_retrieval,
    )

    # 4. Compute Confidence Breakdown
    confidence_breakdown = await confidence_engine.ascore(
        retrieved_chunks=context_chunks,
        aggregated_answer=final_answer,
        agent_responses=agent_responses,
    )

    logger.info(
        f"Council evaluation completed. Final Confidence: {confidence_breakdown.final_score} "
        f"| Aggregated Answer Length: {len(final_answer)} chars."
    )

    return CouncilResponse(
        final_answer=final_answer,
        challenge_critique=challenge_critique,
        confidence=confidence_breakdown,
        agent_responses=agent_responses,
        retrieved_chunks=context_chunks,
    )
