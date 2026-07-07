from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.agent_response import AgentResponse
from app.schemas.council_response import ChallengeCritique, ChunkRef, CouncilResponse
from app.services.agents.aggregator_agent import aggregator_agent
from app.services.agents.challenger_agent import challenger_agent
from app.services.council_pipeline import run_council


def test_aggregator_weight_normalization_and_validation():
    """Test weight normalization across successful agents and validation rules."""
    succ_agents = [
        AgentResponse(agent_name="logical", answer="Ans 1", confidence=0.9),
        AgentResponse(agent_name="rational", answer="Ans 2", confidence=0.9),
        AgentResponse(agent_name="practical", answer="Ans 3", confidence=0.9),
    ]

    # Normalization across successful agents
    raw_weights = {
        "logical": 2.0,
        "rational": 1.0,
        "practical": 1.0,
        "spiritual": 5.0,
    }  # spiritual is not in succ_agents
    norm = aggregator_agent._validate_and_normalize_weights(raw_weights, succ_agents)
    assert norm == {"logical": 0.50, "rational": 0.25, "practical": 0.25}
    assert sum(norm.values()) == 1.0

    # Validation: unknown persona
    with pytest.raises(ValueError, match="Unknown persona name"):
        aggregator_agent._validate_and_normalize_weights({"unknown": 1.0}, succ_agents)

    # Validation: negative weight
    with pytest.raises(ValueError, match="must be non-negative"):
        aggregator_agent._validate_and_normalize_weights({"logical": -1.0}, succ_agents)

    # Validation: infinite weight
    with pytest.raises(ValueError, match="must be a finite numeric value"):
        aggregator_agent._validate_and_normalize_weights(
            {"logical": float("inf")}, succ_agents
        )

    # Validation: all successful agents have 0 weight
    with pytest.raises(
        ValueError, match="At least one successful agent must have a weight > 0"
    ):
        aggregator_agent._validate_and_normalize_weights(
            {"logical": 0.0, "rational": 0.0, "practical": 0.0}, succ_agents
        )


@pytest.mark.asyncio
async def test_challenger_critique():
    """Test structured Challenger critique generation and empty answer fallback."""
    # Empty answer fallback
    crit_empty = await challenger_agent.critique("Q", "", ["chunk 1"])
    assert "No aggregated answer provided" in crit_empty.critique_summary

    # Mocked LLM critique
    mock_json = {
        "critique_summary": "The answer is generally sound but lacks empirical specificity.",
        "weaknesses": ["Relies on broad assumptions without citations."],
        "unsupported_claims": ["Claim about 99% accuracy is not in context."],
        "missing_considerations": ["Overlooks edge case of network latency."],
    }
    with patch(
        "app.services.llm.groq_client.groq_client.generate_json", new_callable=AsyncMock
    ) as mock_gen:
        mock_gen.return_value = mock_json
        crit = await challenger_agent.critique(
            question="How does X work?",
            aggregated_answer="X works by doing Y with 99% accuracy.",
            context_chunks=["Chunk stating X does Y."],
        )
        assert isinstance(crit, ChallengeCritique)
        assert crit.critique_summary == mock_json["critique_summary"]
        assert len(crit.weaknesses) == 1
        assert len(crit.unsupported_claims) == 1
        assert len(crit.missing_considerations) == 1


@pytest.mark.asyncio
async def test_run_council_end_to_end():
    """Test end-to-end run_council pipeline with mocked LLM calls."""
    mock_agents = [
        AgentResponse(
            agent_name="logical", answer="Logical perspective on X.", confidence=0.9
        ),
        AgentResponse(
            agent_name="rational", answer="Rational perspective on X.", confidence=0.9
        ),
    ]
    mock_agg_ans = "Synthesized perspective on X combining logical and rational views."
    mock_crit = ChallengeCritique(
        critique_summary="Solid synthesis.",
        weaknesses=[],
        unsupported_claims=[],
        missing_considerations=[],
    )

    with (
        patch(
            "app.services.agents.agent_orchestrator.agent_orchestrator.run_agents",
            new_callable=AsyncMock,
        ) as mock_run_agents,
        patch(
            "app.services.agents.aggregator_agent.aggregator_agent.aggregate",
            new_callable=AsyncMock,
        ) as mock_agg,
        patch(
            "app.services.agents.challenger_agent.challenger_agent.critique",
            new_callable=AsyncMock,
        ) as mock_crit_call,
    ):

        mock_run_agents.return_value = mock_agents
        mock_agg.return_value = mock_agg_ans
        mock_crit_call.return_value = mock_crit

        chunks = [ChunkRef(content="Context about X.", similarity_score=0.85)]
        response = await run_council(
            question="What is X?",
            context_chunks=chunks,
            user_settings={
                "agent_weights": {
                    "logical": 1.0,
                    "rational": 1.0,
                    "practical": 0.0,
                    "spiritual": 0.0,
                    "skeptical": 0.0,
                }
            },
        )

        assert isinstance(response, CouncilResponse)
        assert response.final_answer == mock_agg_ans
        assert response.challenge_critique == mock_crit
        assert response.agent_responses == mock_agents
        assert response.retrieved_chunks == chunks
        assert 0.0 <= response.confidence.final_score <= 1.0
