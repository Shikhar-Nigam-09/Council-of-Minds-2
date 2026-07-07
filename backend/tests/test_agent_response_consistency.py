import os
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

os.environ["BACKEND_DATABASE_URL"] = "sqlite+aiosqlite:///./test_consistency.db"
os.environ["BACKEND_ENVIRONMENT"] = "testing"

from app.core.database import AsyncSessionLocal, Base, engine
from app.models.user import User
from app.schemas.council_response import ChunkRef
from app.services.agents import LogicalAgent, agent_orchestrator
from app.services.chat_service import ask_question, get_chat_detail
from app.services.council_pipeline import run_council


@pytest.mark.asyncio
async def test_successful_groq_response_produces_valid_agent_response():
    """Prove that a successful Groq response produces AgentResponse(error=None, non-empty answer) even with alternative confidence fields."""
    agent = LogicalAgent()

    # Case 1: Standard confidence field
    mock_resp_1 = {
        "answer": "Valid analysis answer",
        "key_points": ["Point 1"],
        "self_reported_confidence": 0.85,
    }
    with patch(
        "app.services.agents.base_agent.groq_client.generate_json",
        new_callable=AsyncMock,
    ) as mock_gen:
        mock_gen.return_value = mock_resp_1
        res = await agent.respond("Question?", ["Context"])
        assert res.error is None
        assert res.answer == "Valid analysis answer"
        assert res.self_reported_confidence == 0.85

    # Case 2: Alternative field name 'confidence' and string percentage '85%'
    mock_resp_2 = {
        "answer": "Valid analysis answer 2",
        "key_points": ["Point 1"],
        "confidence": "85%",
    }
    with patch(
        "app.services.agents.base_agent.groq_client.generate_json",
        new_callable=AsyncMock,
    ) as mock_gen:
        mock_gen.return_value = mock_resp_2
        res = await agent.respond("Question?", ["Context"])
        assert res.error is None
        assert res.answer == "Valid analysis answer 2"
        assert res.self_reported_confidence == 0.85

    # Case 3: Missing confidence defaults to 0.0 without marking agent failed
    mock_resp_3 = {
        "answer": "Valid analysis answer 3",
        "key_points": ["Point 1"],
    }
    with patch(
        "app.services.agents.base_agent.groq_client.generate_json",
        new_callable=AsyncMock,
    ) as mock_gen:
        mock_gen.return_value = mock_resp_3
        res = await agent.respond("Question?", ["Context"])
        assert res.error is None
        assert res.answer == "Valid analysis answer 3"
        assert res.self_reported_confidence == 0.0


@pytest.mark.asyncio
async def test_orchestrator_success_count_matches_actual_states():
    """Prove that orchestrator success count matches actual AgentResponse states."""
    mock_resp = {
        "answer": "Orchestrated answer",
        "key_points": ["Point A"],
        "score": 80,  # 80% -> 0.8
    }
    with patch(
        "app.services.agents.base_agent.groq_client.generate_json",
        new_callable=AsyncMock,
    ) as mock_gen:
        mock_gen.return_value = mock_resp
        results = await agent_orchestrator.run_agents("Test question", ["Context 1"])
        assert len(results) == 5
        for res in results:
            assert res.error is None
            assert res.answer == "Orchestrated answer"
            assert res.self_reported_confidence == 0.8


@pytest.mark.asyncio
async def test_all_five_successful_agents_remain_successful_through_council_and_persistence():
    """Prove all 5 successful agents remain successful through CouncilResponse, persistence keeps error=NULL, and GET chat returns error=null."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        user = User(
            id=uuid4(),
            email="test_cons@example.com",
            hashed_password="pw",
            full_name="Test User",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    mock_resp = {
        "answer": "Consistent agent answer",
        "key_points": ["Point 1"],
        "self_reported_confidence": 0.0,  # Even with 0 confidence, it is a successful response
    }
    mock_agg_resp = {
        "synthesized_answer": "Final synthesized answer",
        "weights_used": {
            "logical": 0.2,
            "rational": 0.2,
            "practical": 0.2,
            "spiritual": 0.2,
            "skeptical": 0.2,
        },
    }
    mock_challenger_resp = {
        "critique_summary": "Critique summary",
        "weaknesses": ["W1"],
        "unsupported_claims": ["U1"],
        "missing_considerations": ["M1"],
    }

    async def mock_groq_routing(system_prompt, *args, **kwargs):
        if "Aggregator" in system_prompt or "Synthesizer" in system_prompt:
            return mock_agg_resp
        elif "Challenger" in system_prompt or "Devil's Advocate" in system_prompt:
            return mock_challenger_resp
        else:
            return mock_resp

    with (
        patch(
            "app.services.agents.base_agent.groq_client.generate_json",
            side_effect=mock_groq_routing,
        ),
        patch(
            "app.services.agents.aggregator_agent.groq_client.generate_json",
            side_effect=mock_groq_routing,
        ),
        patch(
            "app.services.agents.challenger_agent.groq_client.generate_json",
            side_effect=mock_groq_routing,
        ),
    ):
        # 1. Test CouncilResponse
        chunk = ChunkRef(
            chunk_id=uuid4(), content="Test evidence", similarity_score=0.9
        )
        council_res = await run_council(
            question="What is the truth?",
            context_chunks=[chunk],
            user_settings=None,
        )
        assert len(council_res.agent_responses) == 5
        for a_res in council_res.agent_responses:
            assert a_res.error is None
            assert a_res.answer == "Consistent agent answer"
            assert a_res.self_reported_confidence == 0.0

        # 2. Test Persistence and GET chat serialization
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        async with AsyncSessionLocal() as db:
            stmt = (
                select(User)
                .options(selectinload(User.settings))
                .where(User.id == user.id)
            )
            res = await db.execute(stmt)
            user_in_db = res.scalar_one()
            msg_res = await ask_question(
                db=db, user=user_in_db, question="What is the truth?"
            )
            assert msg_res.status == "success"
            assert len(msg_res.agent_responses) == 6  # 5 personas + 1 challenger

            # Check that reasoning personas have error=None and non-empty answer
            reasoning_agents = [
                r for r in msg_res.agent_responses if r.agent_name != "challenger"
            ]
            assert len(reasoning_agents) == 5
            for r in reasoning_agents:
                assert r.error is None
                assert r.answer == "Consistent agent answer"
                assert r.self_reported_confidence == 0.0

            # Check GET chat API serialization
            chat_detail = await get_chat_detail(
                db=db, user=user_in_db, chat_id=msg_res.chat_id
            )
            assert len(chat_detail.messages) == 2  # user + assistant
            ast_msg = chat_detail.messages[1]
            for r in ast_msg.agent_responses:
                if r.agent_name != "challenger":
                    assert r.error is None
                    assert r.answer == "Consistent agent answer"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
