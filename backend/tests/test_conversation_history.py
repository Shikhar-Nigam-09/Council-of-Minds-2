import asyncio
import os
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ["BACKEND_DATABASE_URL"] = "sqlite+aiosqlite:///./test_history.db"
os.environ["BACKEND_ENVIRONMENT"] = "testing"

from app.core.database import Base
from app.models.chat import Chat
from app.models.message import Message
from app.schemas.agent_response import AgentResponse
from app.services import conversation_context_builder
from app.services.agents import AggregatorAgent, LogicalAgent

engine = create_async_engine("sqlite+aiosqlite:///./test_history.db", echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(autouse=True, scope="module")
def setup_history_db():
    """Setup and teardown isolated test database for history tests."""

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    yield
    if os.path.exists("test_history.db"):
        try:
            os.remove("test_history.db")
        except OSError:
            pass


@pytest.mark.asyncio
async def test_build_history_bounded_and_ordered():
    """Test that build_history retrieves bounded turns in oldest-first chronological order."""
    async with TestingSessionLocal() as db:
        user_id = uuid.uuid4()
        chat = Chat(user_id=user_id, title="History Test")
        db.add(chat)
        await db.commit()
        await db.refresh(chat)

        # Insert 15 messages sequentially
        for i in range(1, 16):
            role = "user" if i % 2 != 0 else "assistant"
            msg = Message(
                chat_id=chat.id,
                role=role,
                content=f"Message turn {i}",
                status="success",
            )
            db.add(msg)
            await db.commit()

        # Build history with limit=10
        history = await conversation_context_builder.build_history(
            db=db, chat_id=chat.id, limit=10
        )
        assert len(history) == 10

        # Verify oldest-first order: should be turns 6 to 15
        contents = [t["content"] for t in history]
        expected = [f"Message turn {i}" for i in range(6, 16)]
        assert contents == expected

        # Test empty returns for None chat_id
        empty_hist = await conversation_context_builder.build_history(
            db=db, chat_id=None
        )
        assert empty_hist == []


@pytest.mark.asyncio
async def test_history_in_agent_prompts():
    """Test that conversation history is formatted into reasoning and aggregator prompts with evidence precedence."""
    history = [
        {"role": "user", "content": "What is Project X?"},
        {"role": "assistant", "content": "Project X is an AI system."},
    ]

    # 1. Test BaseAgent (LogicalAgent) prompt formatting
    agent = LogicalAgent()
    with patch(
        "app.services.agents.base_agent.groq_client.generate_json",
        new_callable=AsyncMock,
    ) as mock_llm:
        mock_llm.return_value = {
            "answer": "Follow-up analysis.",
            "key_points": ["P1"],
            "self_reported_confidence": 0.9,
        }
        await agent.respond(
            question="Who built it?",
            context_chunks=["Chunk 1: Built by Council Team."],
            conversation_history=history,
        )
        assert mock_llm.called
        call_kwargs = mock_llm.call_args.kwargs
        user_prompt = call_kwargs.get("user_prompt", "")

        assert (
            "Recent Conversation History (for resolving follow-up references ONLY):"
            in user_prompt
        )
        assert "[USER]: What is Project X?" in user_prompt
        assert "[ASSISTANT]: Project X is an AI system." in user_prompt
        assert (
            "Prioritize Retrieved Context Evidence over conversational assumptions."
            in user_prompt
        )

    # 2. Test AggregatorAgent prompt formatting
    aggregator = AggregatorAgent()
    with patch(
        "app.services.agents.aggregator_agent.groq_client.generate_json",
        new_callable=AsyncMock,
    ) as mock_agg_llm:
        mock_agg_llm.return_value = {"aggregated_answer": "Synthesized follow-up."}
        dummy_agent = AgentResponse(
            agent_name="logical",
            answer="Logical perspective.",
            key_points=["L1"],
            self_reported_confidence=0.9,
        )
        await aggregator.aggregate(
            question="Who built it?",
            agent_responses=[dummy_agent],
            conversation_history=history,
        )
        assert mock_agg_llm.called
        call_kwargs = mock_agg_llm.call_args.kwargs
        user_prompt = call_kwargs.get("user_prompt", "")

        assert "Recent Conversation History:" in user_prompt
        assert "[USER]: What is Project X?" in user_prompt
        assert (
            "ensure document-grounded evidence takes precedence over conversational assumptions"
            in user_prompt
        )
