import logging
from typing import List

from app.core.config import settings
from app.schemas.agent_response import AgentResponse
from app.schemas.council_response import ChunkRef, ConfidenceBreakdown
from app.services.confidence.agent_agreement import compute_agent_agreement
from app.services.confidence.evidence_coverage import compute_evidence_coverage
from app.services.confidence.retrieval_quality import compute_retrieval_quality

logger = logging.getLogger(__name__)


class ConfidenceEngine:
    """
    Computes the System-Estimated Confidence Score from three normalized signals.

    Important Semantic Note:
    This score is explicitly defined as a deterministic, explainable System-Estimated
    Confidence Score, NOT a probability of correctness. It evaluates architectural
    grounding, retrieval strength, and persona perspective convergence.

    Weighted Sum Formula:
        final_confidence = (retrieval_quality * CONFIDENCE_WEIGHT_RETRIEVAL)
                         + (evidence_coverage * CONFIDENCE_WEIGHT_EVIDENCE)
                         + (agent_agreement   * CONFIDENCE_WEIGHT_AGREEMENT)
    """

    def __init__(self):
        self._validate_weights()

    def _validate_weights(self):
        """Fail-fast validation ensuring weights are non-negative and sum to 1.0."""
        w_ret = settings.CONFIDENCE_WEIGHT_RETRIEVAL
        w_ev = settings.CONFIDENCE_WEIGHT_EVIDENCE
        w_agr = settings.CONFIDENCE_WEIGHT_AGREEMENT

        if w_ret < 0 or w_ev < 0 or w_agr < 0:
            err_msg = (
                f"Confidence weights must be non-negative: retrieval={w_ret}, "
                f"evidence={w_ev}, agreement={w_agr}"
            )
            logger.error(err_msg)
            raise ValueError(err_msg)

        total = w_ret + w_ev + w_agr
        if abs(total - 1.0) > 1e-4:
            err_msg = (
                f"Confidence weights must sum to 1.0 (got {total:.4f}): "
                f"retrieval={w_ret}, evidence={w_ev}, agreement={w_agr}"
            )
            logger.error(err_msg)
            raise ValueError(err_msg)

    def score(
        self,
        retrieved_chunks: List[ChunkRef],
        aggregated_answer: str,
        agent_responses: List[AgentResponse],
    ) -> ConfidenceBreakdown:
        """
        Calculates the three independent signals and combines them into an auditable
        ConfidenceBreakdown object.
        """
        # Ensure weights are valid on every run (in case settings were mutated in tests)
        self._validate_weights()

        w_ret = settings.CONFIDENCE_WEIGHT_RETRIEVAL
        w_ev = settings.CONFIDENCE_WEIGHT_EVIDENCE
        w_agr = settings.CONFIDENCE_WEIGHT_AGREEMENT

        ret_score = compute_retrieval_quality(retrieved_chunks)
        ev_score = compute_evidence_coverage(aggregated_answer, retrieved_chunks)
        agr_score = compute_agent_agreement(agent_responses)

        final_score = (ret_score * w_ret) + (ev_score * w_ev) + (agr_score * w_agr)
        final_score = max(0.0, min(1.0, float(final_score)))

        logger.info(
            f"Confidence Engine scored {final_score:.4f} "
            f"(retrieval={ret_score} * {w_ret}, evidence={ev_score} * {w_ev}, agreement={agr_score} * {w_agr})"
        )

        return ConfidenceBreakdown(
            final_score=round(final_score, 4),
            retrieval_quality=ret_score,
            evidence_coverage=ev_score,
            agent_agreement=agr_score,
            weights_used={
                "retrieval_quality": w_ret,
                "evidence_coverage": w_ev,
                "agent_agreement": w_agr,
            },
        )


confidence_engine = ConfidenceEngine()
