import os
from unittest.mock import patch
from uuid import uuid4

import pytest

os.environ["BACKEND_DATABASE_URL"] = "sqlite+aiosqlite:///./test_rag_bugfix.db"
os.environ["BACKEND_ENVIRONMENT"] = "testing"

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal, Base, engine
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.message_evidence import MessageEvidence
from app.models.user import User
from app.schemas.agent_response import AgentResponse
from app.schemas.council_response import (
    ChallengeCritique,
    ConfidenceBreakdown,
    CouncilResponse,
)
from app.services.chat_service import ask_question
from app.services.rag import index_lifecycle
from app.services.storage.cloudinary_client import cloudinary_client


@pytest.mark.asyncio
async def test_end_to_end_resume_retrieval_bugfix():
    """Prove that indexed resume chunks are successfully retrieved, passed to Council, and persisted as evidence links."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    user_id = uuid4()
    doc_id = uuid4()
    chunk_id_1 = uuid4()
    chunk_id_2 = uuid4()

    async with AsyncSessionLocal() as db:
        user = User(
            id=user_id,
            email="candidate@example.com",
            hashed_password="hashed_pw",
            full_name="Jane Doe",
            is_active=True,
        )
        db.add(user)

        doc = Document(
            id=doc_id,
            user_id=user_id,
            original_filename="jane_doe_resume.pdf",
            cloudinary_public_id="documents/mock_resume.pdf",
            cloudinary_url="documents/mock_resume.pdf",
            file_type="application/pdf",
            file_size_bytes=1024,
            status="ready",
        )
        db.add(doc)

        chunk_1 = DocumentChunk(
            id=chunk_id_1,
            document_id=doc_id,
            user_id=user_id,
            chunk_index=0,
            content="Candidate Summary: Experienced Senior Software Engineer specializing in scalable web architecture, AI agents, and RAG pipelines.",
            faiss_vector_id=str(chunk_id_1),
        )
        chunk_2 = DocumentChunk(
            id=chunk_id_2,
            document_id=doc_id,
            user_id=user_id,
            chunk_index=1,
            content="Technical Skills: Python, FastAPI, React, PostgreSQL, Cloudinary, FAISS, Docker, Kubernetes, AWS, and modern web frameworks.",
            faiss_vector_id=str(chunk_id_2),
        )
        db.add(chunk_1)
        db.add(chunk_2)
        await db.commit()
        await db.refresh(chunk_1)
        await db.refresh(chunk_2)

        # Index the chunks into FAISS for this user
        await index_lifecycle.add_document_chunks_to_index(
            user_id=user_id,
            chunk_objs=[chunk_1, chunk_2],
            storage_client=cloudinary_client,
            db=db,
        )

    # Mock run_council to inspect received context_chunks and return valid response
    received_context_chunks = []

    async def mock_run_council_fn(
        question, context_chunks, user_settings, conversation_history=None
    ):
        nonlocal received_context_chunks
        received_context_chunks = list(context_chunks)
        return CouncilResponse(
            final_answer="The candidate's main technical skills include Python, FastAPI, React, PostgreSQL, and FAISS.",
            challenge_critique=ChallengeCritique(critique_summary="No issues found."),
            confidence=ConfidenceBreakdown(
                final_score=0.92,
                retrieval_quality=0.95,
                evidence_coverage=0.90,
                agent_agreement=0.90,
                weights_used={
                    "retrieval_quality": 0.35,
                    "evidence_coverage": 0.45,
                    "agent_agreement": 0.20,
                },
            ),
            agent_responses=[
                AgentResponse(
                    agent_name="logical",
                    answer="Python and FastAPI are key skills.",
                    self_reported_confidence=0.9,
                )
            ],
            retrieved_chunks=context_chunks,
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

            question = "What are the candidate's main technical skills?"
            msg_res = await ask_question(db=db, user=user_in_db, question=question)

            # 1. Assert retrieval returns at least one chunk and Council receives non-empty context
            assert (
                len(received_context_chunks) > 0
            ), "Expected Council to receive non-empty context chunks!"
            assert any(
                "Python" in c.content or "Technical Skills" in c.content
                for c in received_context_chunks
            )

            # 2. Assert Retrieved Evidence count is greater than 0
            assert (
                len(msg_res.evidence) > 0
            ), "Expected Retrieved Evidence count to be greater than 0!"
            assert len(msg_res.evidence) == len(received_context_chunks)

            # 3. Assert evidence links are persisted in the database
            ev_stmt = select(MessageEvidence).where(
                MessageEvidence.message_id == msg_res.id
            )
            ev_res = await db.execute(ev_stmt)
            persisted_evidence = ev_res.scalars().all()
            assert len(persisted_evidence) == len(msg_res.evidence)
            assert len(persisted_evidence) > 0

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
