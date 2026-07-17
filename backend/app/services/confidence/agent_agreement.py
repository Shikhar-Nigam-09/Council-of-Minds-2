import logging
from typing import List

import numpy as np

from app.schemas.agent_response import AgentResponse
from app.services.rag.embedding_service import embedding_service

logger = logging.getLogger(__name__)


async def acompute_agent_agreement(agent_responses: List[AgentResponse]) -> float:
    """
    Computes the Agent Agreement signal across successful, non-empty agent responses asynchronously.
    """
    valid_responses = [
        res
        for res in agent_responses
        if res.error is None and res.answer and res.answer.strip()
    ]

    if len(valid_responses) <= 1:
        logger.debug(
            f"Agent Agreement: 0.0 ({len(valid_responses)} successful agents; requires >= 2)"
        )
        return 0.0

    answers = [res.answer.strip() for res in valid_responses]
    try:
        # Embed valid answers (shape: N x 384), L2 normalized
        embs = await embedding_service.aembed_texts(answers)

        # Compute cosine similarity matrix (shape: N x N) via dot product
        sim_matrix = np.dot(embs, embs.T)

        # Extract upper triangle indices excluding diagonal
        n = len(valid_responses)
        upper_indices = np.triu_indices(n, k=1)
        pairwise_sims = sim_matrix[upper_indices]

        clamped_sims = np.clip(pairwise_sims, 0.0, 1.0)
        mean_agreement = float(np.mean(clamped_sims))
        logger.debug(
            f"Agent Agreement: {mean_agreement:.4f} across {len(valid_responses)} successful agents ({len(pairwise_sims)} pairs)"
        )
        return round(mean_agreement, 4)
    except Exception as exc:
        logger.error(
            f"Error computing agent agreement: {exc}. Falling back to 0.0.",
            exc_info=True,
        )
        return 0.0


def compute_agent_agreement(agent_responses: List[AgentResponse]) -> float:
    """Synchronous wrapper for acompute_agent_agreement."""
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None and loop.is_running():
        raise RuntimeError(
            "compute_agent_agreement() cannot be called from an active async event loop. "
            "Use 'await acompute_agent_agreement()' instead."
        )
    return asyncio.run(acompute_agent_agreement(agent_responses))
