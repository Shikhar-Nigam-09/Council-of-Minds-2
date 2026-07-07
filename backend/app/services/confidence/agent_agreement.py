import logging
from typing import List

import numpy as np

from app.schemas.agent_response import AgentResponse
from app.services.rag.embedding_service import embedding_service

logger = logging.getLogger(__name__)


def compute_agent_agreement(agent_responses: List[AgentResponse]) -> float:
    """
    Computes the Agent Agreement signal across successful, non-empty agent responses.

    Important Semantic Note:
    This signal measures **perspective convergence** across the five reasoning personas,
    not proof of factual correctness. When multiple personas with different reasoning styles
    (e.g., Logical vs. Skeptical vs. Practical) converge on semantically similar conclusions,
    it indicates high inter-agent consensus and architectural stability.

    Methodology & Edge Cases:
    1. Filter the input responses to include only successful, non-empty answers where:
           response.error is None and response.answer.strip() != ""
    2. If there are 0 or 1 successful agents (N <= 1), pairwise agreement cannot be computed,
       so we return 0.0 immediately as defined by our system specification.
    3. We embed the N valid answer strings using our L2-normalized MiniLM model.
    4. We compute the N x N inner product matrix (which equals exact cosine similarity).
    5. We extract the upper triangle of the similarity matrix (excluding the diagonal),
       representing all N * (N - 1) / 2 unique pairwise similarities.
    6. Agent Agreement is the arithmetic mean of these pairwise similarities, clamped to [0.0, 1.0].
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
        embs = embedding_service.embed_texts(answers)

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
