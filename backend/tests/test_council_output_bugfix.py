import os
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

os.environ["BACKEND_DATABASE_URL"] = "sqlite+aiosqlite:///./test_council_output.db"
os.environ["BACKEND_ENVIRONMENT"] = "testing"

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal, Base, engine
from app.models.user import User
from app.schemas.agent_response import AgentResponse
from app.schemas.council_response import (
    ChallengeCritique,
    ConfidenceBreakdown,
    CouncilResponse,
)
from app.services.agents.aggregator_agent import aggregator_agent
from app.services.agents.challenger_agent import challenger_agent
from app.services.chat_service import ask_question, get_chat_detail
from app.services.llm.groq_client import GroqClient


@pytest.mark.asyncio
async def test_groq_client_generate_json_accepts_model_and_model_name():
    """Verify GroqClient.generate_json accepts model and model_name keyword args without error."""
    client = GroqClient(api_key="test_key")

    mock_create = AsyncMock()
    mock_create.return_value.choices = [
        type("obj", (), {"message": type("msg", (), {"content": '{"test": "ok"}'})()})()
    ]
    client.client = type(
        "mock_client",
        (),
        {
            "chat": type(
                "chat", (), {"completions": type("comp", (), {"create": mock_create})()}
            )()
        },
    )()

    # Test passing model=...
    res1 = await client.generate_json(
        system_prompt="sys", user_prompt="usr", model="test-model-1"
    )
    assert res1 == {"test": "ok"}
    mock_create.assert_called_with(
        model="test-model-1",
        messages=[
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "usr"},
        ],
        temperature=0.7,
        max_tokens=1024,
        response_format={"type": "json_object"},
    )

    # Test passing model_name=...
    res2 = await client.generate_json(
        system_prompt="sys", user_prompt="usr", model_name="test-model-2"
    )
    assert res2 == {"test": "ok"}
    mock_create.assert_called_with(
        model="test-model-2",
        messages=[
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "usr"},
        ],
        temperature=0.7,
        max_tokens=1024,
        response_format={"type": "json_object"},
    )


@pytest.mark.asyncio
async def test_aggregator_produces_non_empty_answer():
    """Verify five successful agents produce a non-empty aggregated final answer."""
    agents = [
        AgentResponse(
            agent_name="logical",
            answer="Logical view",
            key_points=["L1"],
            self_reported_confidence=0.9,
        ),
        AgentResponse(
            agent_name="rational",
            answer="Rational view",
            key_points=["R1"],
            self_reported_confidence=0.85,
        ),
        AgentResponse(
            agent_name="practical",
            answer="Practical view",
            key_points=["P1"],
            self_reported_confidence=0.88,
        ),
        AgentResponse(
            agent_name="spiritual",
            answer="Spiritual view",
            key_points=["S1"],
            self_reported_confidence=0.8,
        ),
        AgentResponse(
            agent_name="skeptical",
            answer="Skeptical view",
            key_points=["K1"],
            self_reported_confidence=0.75,
        ),
    ]

    mock_generate = AsyncMock(
        return_value={
            "aggregated_answer": "This is a comprehensive, synthesized final answer."
        }
    )
    with patch(
        "app.services.agents.aggregator_agent.groq_client.generate_json", mock_generate
    ):
        ans = await aggregator_agent.aggregate(
            question="Test question?", agent_responses=agents
        )
        assert ans == "This is a comprehensive, synthesized final answer."
        assert len(ans) > 0
        assert mock_generate.call_args[1]["model"] is not None


@pytest.mark.asyncio
async def test_challenger_produces_populated_critique():
    """Verify Challenger produces a populated critique with summary, weaknesses, unsupported claims, and missing considerations."""
    mock_generate = AsyncMock(
        return_value={
            "critique_summary": "The answer is generally sound but lacks empirical backing on scalability.",
            "weaknesses": [
                "Assumes linear scaling without considering database contention."
            ],
            "unsupported_claims": [
                "Claiming 99.99% uptime is not supported by the context."
            ],
            "missing_considerations": ["Need to consider disaster recovery protocols."],
        }
    )
    with patch(
        "app.services.agents.challenger_agent.groq_client.generate_json", mock_generate
    ):
        crit = await challenger_agent.critique(
            question="How scalable is the architecture?",
            aggregated_answer="The architecture scales linearly and achieves 99.99% uptime.",
            context_chunks=["The system uses PostgreSQL and Docker."],
        )
        assert (
            crit.critique_summary
            == "The answer is generally sound but lacks empirical backing on scalability."
        )
        assert len(crit.weaknesses) == 1
        assert len(crit.unsupported_claims) == 1
        assert len(crit.missing_considerations) == 1
        assert mock_generate.call_args[1]["model"] is not None


@pytest.mark.asyncio
async def test_end_to_end_persistence_and_get_chat_serialization():
    """Verify aggregated answer and challenger critique survive persistence and GET chat serialization."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    user_id = uuid4()
    async with AsyncSessionLocal() as db:
        user = User(
            id=user_id,
            email="tester@example.com",
            hashed_password="hashed_pw",
            full_name="Test User",
            is_active=True,
        )
        db.add(user)
        await db.commit()

    async def mock_run_council_fn(
        question, context_chunks, user_settings, conversation_history=None
    ):
        return CouncilResponse(
            final_answer="Aggregated final answer from council.",
            challenge_critique=ChallengeCritique(
                critique_summary="Challenger red-team summary.",
                weaknesses=["Weakness 1"],
                unsupported_claims=["Unsupported 1"],
                missing_considerations=["Missing 1"],
            ),
            confidence=ConfidenceBreakdown(
                final_score=0.9,
                retrieval_quality=0.9,
                evidence_coverage=0.9,
                agent_agreement=0.9,
                weights_used={
                    "retrieval_quality": 0.35,
                    "evidence_coverage": 0.45,
                    "agent_agreement": 0.20,
                },
            ),
            agent_responses=[
                AgentResponse(
                    agent_name="logical",
                    answer="Logical answer",
                    key_points=["L1"],
                    self_reported_confidence=0.9,
                ),
                AgentResponse(
                    agent_name="rational",
                    answer="Rational answer",
                    key_points=["R1"],
                    self_reported_confidence=0.85,
                ),
            ],
            retrieved_chunks=[],
        )

    with patch(
        "app.services.chat_service.run_council", side_effect=mock_run_council_fn
    ):
        async with AsyncSessionLocal() as db:
            stmt = (
                select(User)
                .options(selectinload(User.settings))
                .where(User.id == user_id)
            )
            res = await db.execute(stmt)
            user_in_db = res.scalar_one()

            msg_res = await ask_question(
                db=db, user=user_in_db, question="Test question?"
            )
            chat_id = msg_res.chat_id

            # Verify GET chat detail serialization
            chat_detail = await get_chat_detail(db=db, user=user_in_db, chat_id=chat_id)
            assert len(chat_detail.messages) == 2
            assistant_msg = chat_detail.messages[1]
            assert assistant_msg.role == "assistant"
            assert assistant_msg.content == "Aggregated final answer from council."

            # Verify challenger in agent_responses
            challenger_resp = next(
                (
                    a
                    for a in assistant_msg.agent_responses
                    if a.agent_name == "challenger"
                ),
                None,
            )
            assert challenger_resp is not None
            assert challenger_resp.answer == "Challenger red-team summary."
            assert isinstance(challenger_resp.key_points, dict)
            assert challenger_resp.key_points["weaknesses"] == ["Weakness 1"]
            assert challenger_resp.key_points["unsupported_claims"] == ["Unsupported 1"]
            assert challenger_resp.key_points["missing_considerations"] == ["Missing 1"]

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
