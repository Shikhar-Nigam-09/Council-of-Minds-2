from app.core.config import settings
from app.schemas.agent_response import AgentResponse
from app.schemas.council_response import ChunkRef, ConfidenceBreakdown
from app.services.confidence.agent_agreement import compute_agent_agreement
from app.services.confidence.confidence_engine import confidence_engine
from app.services.confidence.evidence_coverage import compute_evidence_coverage
from app.services.confidence.retrieval_quality import compute_retrieval_quality


def test_retrieval_quality_signal():
    """Test retrieval quality normalization and empty retrieval fallback."""
    # Empty retrieval -> 0.0
    assert compute_retrieval_quality([]) == 0.0

    # Normal scores
    chunks = [
        ChunkRef(content="chunk 1", similarity_score=0.80),
        ChunkRef(content="chunk 2", similarity_score=0.90),
    ]
    assert compute_retrieval_quality(chunks) == 0.85

    # Clamping out-of-bounds scores
    clamped_chunks = [
        ChunkRef(content="chunk 1", similarity_score=-0.20),  # clamped to 0.0
        ChunkRef(content="chunk 2", similarity_score=1.50),  # clamped to 1.0
    ]
    assert compute_retrieval_quality(clamped_chunks) == 0.50


def test_evidence_coverage_signal():
    """Test evidence coverage heuristic and empty edge cases."""
    # Empty chunks or empty answer -> 0.0
    assert compute_evidence_coverage("Some answer", []) == 0.0
    assert compute_evidence_coverage("", [ChunkRef(content="chunk 1")]) == 0.0

    # Grounded answer against matching chunk
    chunks = [
        ChunkRef(
            content="The Council of Minds is an advanced multi-agent RAG system built with FastAPI and React."
        )
    ]
    grounded_answer = "The Council of Minds is a multi-agent RAG system developed using FastAPI and React."
    cov_score = compute_evidence_coverage(grounded_answer, chunks)
    assert (
        cov_score > 0.70
    ), f"Expected high coverage for grounded text, got {cov_score}"


def test_agent_agreement_signal():
    """Test perspective convergence across successful agents and edge cases (0 or 1 agent -> 0.0)."""
    # 0 or 1 successful agent -> 0.0
    assert compute_agent_agreement([]) == 0.0
    assert (
        compute_agent_agreement(
            [
                AgentResponse(
                    agent_name="logical", answer="Single answer", confidence=0.9
                )
            ]
        )
        == 0.0
    )

    # Failed agents ignored
    res_failed = [
        AgentResponse(agent_name="logical", answer="Valid answer", confidence=0.9),
        AgentResponse(
            agent_name="rational", answer="", error="Timeout", confidence=0.0
        ),
    ]
    assert compute_agent_agreement(res_failed) == 0.0

    # High agreement across 3 converging agents
    res_converging = [
        AgentResponse(
            agent_name="logical",
            answer="The sky appears blue due to Rayleigh scattering of sunlight in the atmosphere.",
            confidence=0.9,
        ),
        AgentResponse(
            agent_name="rational",
            answer="Rayleigh scattering causes solar radiation to scatter, making the clear sky look blue.",
            confidence=0.9,
        ),
        AgentResponse(
            agent_name="practical",
            answer="Sunlight scattering in Earth's atmosphere is responsible for the blue sky.",
            confidence=0.9,
        ),
    ]
    agr_score = compute_agent_agreement(res_converging)
    assert (
        agr_score > 0.70
    ), f"Expected high agreement for converging answers, got {agr_score}"


def test_confidence_engine_weighted_sum(monkeypatch):
    """Test exact weighted sum calculation and ConfidenceBreakdown structure."""
    chunks = [
        ChunkRef(
            content="Context chunk about Python and FastAPI.", similarity_score=0.80
        )
    ]
    answer = "Python and FastAPI are used in this project."
    agents = [
        AgentResponse(
            agent_name="logical", answer="Python and FastAPI are used.", confidence=0.9
        ),
        AgentResponse(
            agent_name="rational", answer="We use Python and FastAPI.", confidence=0.9
        ),
    ]

    breakdown = confidence_engine.score(
        retrieved_chunks=chunks,
        aggregated_answer=answer,
        agent_responses=agents,
    )

    assert isinstance(breakdown, ConfidenceBreakdown)
    assert 0.0 <= breakdown.final_score <= 1.0
    assert breakdown.retrieval_quality == 0.80

    # Verify mathematical formula
    w_ret = settings.CONFIDENCE_WEIGHT_RETRIEVAL
    w_ev = settings.CONFIDENCE_WEIGHT_EVIDENCE
    w_agr = settings.CONFIDENCE_WEIGHT_AGREEMENT
    expected = round(
        (breakdown.retrieval_quality * w_ret)
        + (breakdown.evidence_coverage * w_ev)
        + (breakdown.agent_agreement * w_agr),
        4,
    )
    assert breakdown.final_score == expected
