import asyncio
import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

os.environ["BACKEND_DATABASE_URL"] = "sqlite+aiosqlite:///./test_chat.db"
os.environ["BACKEND_ENVIRONMENT"] = "testing"

from app.core.database import Base, engine
from app.main import app
from app.schemas.agent_response import AgentResponse as AgentResponseSchema
from app.schemas.council_response import (
    ChallengeCritique,
    ConfidenceBreakdown,
    CouncilResponse,
)

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def setup_chat_db():
    """Setup and teardown isolated test database for chat flow tests."""

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())
    yield
    if os.path.exists("test_chat.db"):
        try:
            os.remove("test_chat.db")
        except OSError:
            pass


def get_auth_headers(email: str, name: str) -> dict:
    """Helper to register/login a user and return Bearer auth headers."""
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!", "full_name": name},
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_council_response():
    """Creates a mock successful CouncilResponse object."""
    agent_responses = [
        AgentResponseSchema(
            agent_name="logical",
            answer="Logical answer",
            key_points=["L1", "L2"],
            self_reported_confidence=0.9,
            latency_ms=100,
        ),
        AgentResponseSchema(
            agent_name="rational",
            answer="Rational answer",
            key_points=["R1"],
            self_reported_confidence=0.85,
            latency_ms=110,
        ),
        AgentResponseSchema(
            agent_name="practical",
            answer="Practical answer",
            key_points=["P1"],
            self_reported_confidence=0.8,
            latency_ms=90,
        ),
        AgentResponseSchema(
            agent_name="spiritual",
            answer="Spiritual answer",
            key_points=["S1"],
            self_reported_confidence=0.75,
            latency_ms=95,
        ),
        AgentResponseSchema(
            agent_name="skeptical",
            answer="Skeptical answer",
            key_points=["Sk1"],
            self_reported_confidence=0.7,
            latency_ms=105,
        ),
    ]
    confidence = ConfidenceBreakdown(
        retrieval_quality=0.8,
        evidence_coverage=0.85,
        agent_agreement=0.9,
        final_score=0.85,
        weights_used={"retrieval": 0.35, "evidence": 0.45, "agreement": 0.20},
    )
    critique = ChallengeCritique(
        weaknesses=["None major"],
        unsupported_claims=[],
        missing_considerations=["Timeframe"],
        critique_summary="Overall solid answer.",
    )
    return CouncilResponse(
        question="Test question?",
        retrieved_chunks=[],
        agent_responses=agent_responses,
        final_answer="Synthesized council answer.",
        challenge_critique=critique,
        confidence=confidence,
    )


def test_end_to_end_chat_flow(mock_council_response):
    """Test creating chat, sending messages, listing chats, and viewing chat details."""
    headers = get_auth_headers("chatuser@example.com", "Chat User")

    with patch(
        "app.services.chat_service.run_council", new_callable=AsyncMock
    ) as mock_run:
        mock_run.return_value = mock_council_response

        # 1. Send first message (creates new chat)
        res1 = client.post(
            "/api/v1/chats/messages",
            headers=headers,
            json={"question": "What is AI?"},
        )
        assert res1.status_code == 201, res1.text
        data1 = res1.json()
        assert data1["role"] == "assistant"
        assert data1["content"] == "Synthesized council answer."
        assert data1["status"] == "success"
        assert data1["confidence_score"] == 0.85
        assert len(data1["agent_responses"]) == 6  # 5 personas + 1 challenger
        chat_id = data1["chat_id"]

        # Verify challenger critique is included in agent_responses
        challenger_row = next(
            r for r in data1["agent_responses"] if r["agent_name"] == "challenger"
        )
        assert challenger_row["answer"] == "Overall solid answer."
        assert "weaknesses" in challenger_row["key_points"]

        # 2. List user chats
        list_res = client.get("/api/v1/chats", headers=headers)
        assert list_res.status_code == 200, list_res.text
        chats = list_res.json()
        assert len(chats) >= 1
        assert any(c["id"] == chat_id for c in chats)

        # 3. Send follow-up message to same chat
        res2 = client.post(
            "/api/v1/chats/messages",
            headers=headers,
            json={"question": "Tell me more.", "chat_id": chat_id},
        )
        assert res2.status_code == 201, res2.text
        data2 = res2.json()
        assert data2["chat_id"] == chat_id

        # 4. Get chat details (should have 4 chronological messages: U, A, U, A)
        detail_res = client.get(f"/api/v1/chats/{chat_id}", headers=headers)
        assert detail_res.status_code == 200, detail_res.text
        detail = detail_res.json()
        assert detail["id"] == chat_id
        assert len(detail["messages"]) == 4
        roles = [m["role"] for m in detail["messages"]]
        assert roles == ["user", "assistant", "user", "assistant"]


def test_atomic_persistence_and_failure_state(mock_council_response):
    """
    Test that when Council evaluation fails, the user's question remains persisted
    and marked with status='failed', and NO assistant message or partial agent rows are saved.
    """
    headers = get_auth_headers("failuser@example.com", "Fail User")

    with patch(
        "app.services.chat_service.run_council", new_callable=AsyncMock
    ) as mock_run:
        # 1. Create chat with successful first turn
        mock_run.return_value = mock_council_response
        res1 = client.post(
            "/api/v1/chats/messages",
            headers=headers,
            json={"question": "Initial question."},
        )
        assert res1.status_code == 201, res1.text
        chat_id = res1.json()["chat_id"]

        # 2. Simulate Council failure on second turn
        mock_run.side_effect = Exception("LLM Provider Timeout")
        res2 = client.post(
            "/api/v1/chats/messages",
            headers=headers,
            json={"question": "Failing question.", "chat_id": chat_id},
        )
        assert res2.status_code == 500
        assert "Council evaluation failed" in res2.text

        # 3. Verify chat details: exactly 3 messages (U, A, failed U), NO assistant row
        detail_res = client.get(f"/api/v1/chats/{chat_id}", headers=headers)
        assert detail_res.status_code == 200, detail_res.text
        messages = detail_res.json()["messages"]
        assert len(messages) == 3

        last_msg = messages[-1]
        assert last_msg["role"] == "user"
        assert last_msg["content"] == "Failing question."
        assert last_msg["status"] == "failed"
        assert len(last_msg["agent_responses"]) == 0


def test_delete_chat():
    """Test cascade deletion of a chat session."""
    headers = get_auth_headers("deluser@example.com", "Del User")

    with patch(
        "app.services.chat_service.run_council", new_callable=AsyncMock
    ) as mock_run:
        mock_run.return_value = CouncilResponse(
            question="Q?",
            retrieved_chunks=[],
            agent_responses=[],
            final_answer="A.",
            challenge_critique=ChallengeCritique(
                weaknesses=[],
                unsupported_claims=[],
                missing_considerations=[],
                critique_summary="",
            ),
            confidence=ConfidenceBreakdown(
                retrieval_quality=0,
                evidence_coverage=0,
                agent_agreement=0,
                final_score=0,
                weights_used={},
            ),
        )
        res = client.post(
            "/api/v1/chats/messages",
            headers=headers,
            json={"question": "To be deleted."},
        )
        chat_id = res.json()["chat_id"]

        # Delete chat
        del_res = client.delete(f"/api/v1/chats/{chat_id}", headers=headers)
        assert del_res.status_code == 204

        # Verify 404 on get
        get_res = client.get(f"/api/v1/chats/{chat_id}", headers=headers)
        assert get_res.status_code == 404
