import asyncio
import time
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.schemas.agent_response import AgentResponse
from app.schemas.council_response import (
    ChallengeCritique,
    ChunkRef,
    ConfidenceBreakdown,
    CouncilResponse,
)
from app.services.agents import (
    LogicalAgent,
    PracticalAgent,
    RationalAgent,
    SkepticalAgent,
    SpiritualAgent,
    agent_orchestrator,
)

client = TestClient(app)


def test_agent_response_schema():
    """Verify AgentResponse schema validation and metadata confidence handling."""
    res = AgentResponse(
        agent_name="test",
        answer="Sample analysis",
        key_points=["Point 1", "Point 2"],
        self_reported_confidence=0.85,
        latency_ms=120.5,
    )
    assert res.agent_name == "test"
    assert res.self_reported_confidence == 0.85
    assert res.error is None

    # Test default error state
    err_res = AgentResponse(
        agent_name="test_err",
        error="API failure",
    )
    assert err_res.answer == ""
    assert err_res.key_points == []
    assert err_res.self_reported_confidence == 0.0
    assert err_res.error == "API failure"


@pytest.mark.asyncio
async def test_individual_agents():
    """Test that all five agents correctly format prompts and produce valid AgentResponses."""
    agents = [
        LogicalAgent(),
        RationalAgent(),
        PracticalAgent(),
        SpiritualAgent(),
        SkepticalAgent(),
    ]

    mock_response = {
        "answer": "This is a detailed analysis from the persona.",
        "key_points": ["First point", "Second point", "Third point"],
        "self_reported_confidence": 0.9,
    }

    with patch(
        "app.services.agents.base_agent.groq_client.generate_json",
        new_callable=AsyncMock,
    ) as mock_generate:
        mock_generate.return_value = mock_response

        for agent in agents:
            res = await agent.respond(
                question="What is our strategic priority?",
                context_chunks=[
                    "Chunk A: Focus on growth.",
                    "Chunk B: Ensure stability.",
                ],
            )
            assert res.agent_name == agent.name
            assert res.answer == mock_response["answer"]
            assert res.key_points == mock_response["key_points"]
            assert res.self_reported_confidence == 0.9
            assert res.error is None
            assert res.latency_ms > 0

        assert mock_generate.call_count == 5


@pytest.mark.asyncio
async def test_orchestrator_parallel_execution():
    """Verify that run_agents executes all five agents concurrently via asyncio.gather()."""

    async def mock_delayed_generate(*args, **kwargs):
        await asyncio.sleep(0.1)  # 100ms artificial delay per agent
        return {
            "answer": "Parallel response",
            "key_points": ["Point"],
            "self_reported_confidence": 0.8,
        }

    with patch(
        "app.services.agents.base_agent.groq_client.generate_json",
        side_effect=mock_delayed_generate,
    ):
        start_time = time.perf_counter()
        results = await agent_orchestrator.run_agents(
            question="Test parallel speed",
            context_chunks=["Context 1", "Context 2"],
        )
        elapsed = time.perf_counter() - start_time

        assert len(results) == 5
        for res in results:
            assert res.error is None
            assert res.answer == "Parallel response"

        # Sequential would take > 0.5 seconds (5 * 0.1s).
        # Parallel via asyncio.gather should finish in ~0.1s (allowing up to 0.35s for overhead).
        assert (
            elapsed < 0.35
        ), f"Expected parallel execution under 0.35s, took {elapsed:.2f}s"


@pytest.mark.asyncio
async def test_orchestrator_error_isolation():
    """Verify that simulated failures or timeouts in individual agents do not break the batch."""
    call_count = 0

    async def mock_failing_generate(system_prompt, *args, **kwargs):
        nonlocal call_count
        call_count += 1
        if "Logical Agent" in system_prompt:
            raise RuntimeError("Groq API 500 Server Error")
        elif "Rational Agent" in system_prompt:
            await asyncio.sleep(10)  # Will trigger timeout
            return {"answer": "Should not reach"}
        else:
            return {
                "answer": "Successful analysis",
                "key_points": ["Valid point"],
                "self_reported_confidence": 0.75,
            }

    with (
        patch(
            "app.services.agents.base_agent.groq_client.generate_json",
            side_effect=mock_failing_generate,
        ),
        patch.object(settings, "AGENT_TIMEOUT_SECONDS", 0.2),
    ):  # Shorten timeout for test
        results = await agent_orchestrator.run_agents(
            question="Test error isolation",
            context_chunks=["Context chunk"],
        )

        assert len(results) == 5
        results_by_name = {r.agent_name: r for r in results}

        # Logical agent failed with exception
        logical_res = results_by_name["logical"]
        assert logical_res.error is not None
        assert "Groq API 500 Server Error" in logical_res.error
        assert logical_res.answer == ""

        # Rational agent failed with timeout
        rational_res = results_by_name["rational"]
        assert rational_res.error is not None
        assert "timed out" in rational_res.error
        assert rational_res.answer == ""

        # Other three agents succeeded normally
        for name in ["practical", "spiritual", "skeptical"]:
            res = results_by_name[name]
            assert res.error is None
            assert res.answer == "Successful analysis"
            assert res.self_reported_confidence == 0.75


def test_dev_endpoint_gating():
    """Verify dev endpoint works in dev/test mode and returns HTTP 403 in production mode."""
    mock_response_data = [
        {
            "agent_name": "logical",
            "answer": "Test answer",
            "key_points": ["Point 1"],
            "self_reported_confidence": 0.9,
            "latency_ms": 50.0,
            "error": None,
        }
    ]

    mock_council_response = CouncilResponse(
        final_answer="Aggregated answer",
        challenge_critique=ChallengeCritique(critique_summary="Critique"),
        confidence=ConfidenceBreakdown(
            final_score=0.85,
            retrieval_quality=0.80,
            evidence_coverage=0.90,
            agent_agreement=0.85,
            weights_used={
                "retrieval_quality": 0.35,
                "evidence_coverage": 0.45,
                "agent_agreement": 0.20,
            },
        ),
        agent_responses=[AgentResponse(**mock_response_data[0])],
        retrieved_chunks=[ChunkRef(content="Chunk 1", similarity_score=0.85)],
    )

    with patch(
        "app.api.v1.dev_agents.run_council",
        new_callable=AsyncMock,
    ) as mock_run:
        mock_run.return_value = mock_council_response

        # 1. Test in development mode
        with patch.object(settings, "ENVIRONMENT", "development"):
            response = client.post(
                "/api/v1/dev/agents/test",
                json={
                    "question": "Dev test question",
                    "context_chunks": ["Chunk 1"],
                    "document_id": str(uuid4()),
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data["final_answer"] == "Aggregated answer"
            assert len(data["agent_responses"]) == 1
            assert data["agent_responses"][0]["agent_name"] == "logical"

        # 2. Test in production mode
        with patch.object(settings, "ENVIRONMENT", "production"):
            prod_response = client.post(
                "/api/v1/dev/agents/test",
                json={
                    "question": "Should be blocked",
                    "context_chunks": ["Chunk 1"],
                },
            )
            assert prod_response.status_code == 403
            assert "disabled in production" in prod_response.json()["detail"]
