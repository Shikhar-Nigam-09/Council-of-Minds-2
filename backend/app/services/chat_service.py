import logging
import uuid
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.config import settings
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.repositories.agent_response_repository import AgentResponseRepository
from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.agent_response import AgentResponse as AgentResponseSchema
from app.schemas.chat import ChatDetail, ChatSummary
from app.schemas.council_response import ChunkRef
from app.schemas.message import MessageResponse
from app.services import conversation_context_builder
from app.services.council_pipeline import run_council
from app.services.rag import index_lifecycle, vector_store
from app.services.rag.embedding_service import embedding_service
from app.services.storage.cloudinary_client import cloudinary_client

logger = logging.getLogger(__name__)


async def ask_question(
    db: AsyncSession,
    user: User,
    question: str,
    chat_id: Optional[uuid.UUID | str] = None,
) -> MessageResponse:
    """
    Orchestrates the complete end-to-end question answering pipeline:
    1. Creates new chat session if chat_id is None.
    2. Persists the user question message immediately.
    3. Builds bounded conversation history (excluding current question).
    4. Composes Contextual Retrieval Query (recent turns + question) and searches FAISS.
    5. Evaluates query and context via Council of Minds.
    6. Atomically persists assistant reply, 5 persona outputs + challenger critique, and evidence links.
    7. Handles Council/persistence failures by marking user message as failed.
    """
    chat_repo = ChatRepository(db)
    msg_repo = MessageRepository(db)
    agent_repo = AgentResponseRepository(db)

    # 1. Resolve or create chat session
    if chat_id is None:
        title = question[:50].strip() or "New Chat"
        chat = await chat_repo.create(user_id=user.id, title=title)
        chat_id = chat.id
        logger.info(f"Created new chat session {chat_id} for user {user.id}")
    else:
        if isinstance(chat_id, str):
            chat_id = uuid.UUID(chat_id)
        chat = await chat_repo.get_by_id_for_user(chat_id=chat_id, user_id=user.id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found or access denied.",
            )

    # 2. Persist user question message immediately
    user_msg = await msg_repo.create(
        chat_id=chat_id,
        role="user",
        content=question,
        status="success",
        commit=True,
    )

    # 3. Build bounded conversation history
    history = await conversation_context_builder.build_history(
        db=db,
        chat_id=chat_id,
        limit=settings.MAX_CHAT_HISTORY_MESSAGES,
    )
    # Exclude the just-inserted user message from historical context
    history_turns = (
        history[:-1]
        if (
            history
            and history[-1]["role"] == "user"
            and history[-1]["content"] == question
        )
        else history
    )

    # 4. Contextual Retrieval Query (Essential)
    if history_turns:
        recent_str = " | ".join(
            [f"{t['role'].upper()}: {t['content']}" for t in history_turns[-3:]]
        )
        retrieval_query_str = f"Context: {recent_str} | Current Question: {question}"
        logger.debug(
            f"Composed contextual retrieval query for FAISS search: '{retrieval_query_str[:100]}...'"
        )
    else:
        retrieval_query_str = question

    chunk_refs: List[ChunkRef] = []
    try:
        query_vector = embedding_service.embed_query(retrieval_query_str)
        logger.info(
            f"[Diagnostic Retrieval] query embedding shape: {query_vector.shape}, dtype: {query_vector.dtype}"
        )
        index, metadata = await index_lifecycle.get_or_recover_index(
            user_id=user.id, db=db, storage_client=cloudinary_client
        )
        index_size = index.ntotal if index is not None else 0
        logger.info(f"[Diagnostic Retrieval] FAISS index size: {index_size}")
        search_res = vector_store.search(
            user_id=user.id,
            index=index,
            metadata=metadata,
            query_vector=query_vector,
            top_k=5,
        )

        search_results_count = len(search_res.get("results", []))
        vector_ids = [r["chunk_id"] for r in search_res.get("results", [])]
        logger.info(
            f"[Diagnostic Retrieval] number of search results: {search_results_count}"
        )
        logger.info(f"[Diagnostic Retrieval] returned vector IDs: {vector_ids}")

        if search_res.get("status") == "success" and search_res.get("results"):
            chunk_uuids = [uuid.UUID(r["chunk_id"]) for r in search_res["results"]]
            stmt = (
                select(DocumentChunk)
                .options(joinedload(DocumentChunk.document))
                .where(DocumentChunk.id.in_(chunk_uuids))
            )
            db_res = await db.execute(stmt)
            chunks_map = {str(c.id): c for c in db_res.scalars().all()}
            logger.info(
                f"[Diagnostic Retrieval] number of PostgreSQL chunks resolved: {len(chunks_map)}"
            )

            for r in search_res["results"]:
                cid_str = str(r["chunk_id"])
                if cid_str in chunks_map:
                    c = chunks_map[cid_str]
                    chunk_refs.append(
                        ChunkRef(
                            chunk_id=c.id,
                            content=c.content,
                            similarity_score=float(r["score"]),
                            document_name=(
                                c.document.original_filename if c.document else None
                            ),
                        )
                    )
        else:
            logger.info(
                f"Vector retrieval returned status: {search_res.get('status', 'empty')} for query."
            )
            logger.info(
                "[Diagnostic Retrieval] number of PostgreSQL chunks resolved: 0"
            )

        logger.info(
            f"[Diagnostic Retrieval] final ChunkRef count passed to Council: {len(chunk_refs)}"
        )
    except Exception as exc:
        logger.error(
            f"Vector retrieval failed for user {user.id}: {exc}", exc_info=True
        )
        if settings.ENVIRONMENT in ["development", "testing"]:
            await msg_repo.update_status(user_msg, status="failed", commit=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Vector retrieval failed: {str(exc)}",
            )
        chunk_refs = []

    # 5. Execute Council Evaluation
    try:
        council_res = await run_council(
            question=question,
            context_chunks=chunk_refs,
            user_settings=user.settings,
            conversation_history=history_turns,
        )
    except Exception as exc:
        logger.error(
            f"Council evaluation failed for chat {chat_id}: {exc}", exc_info=True
        )
        await msg_repo.update_status(user_msg, status="failed", commit=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Council evaluation failed: {str(exc)}",
        )

    # 6. Atomic Persistence of Assistant Reply, Agents, and Evidence
    try:
        assistant_msg = await msg_repo.create(
            chat_id=chat_id,
            role="assistant",
            content=council_res.final_answer,
            status="success",
            confidence_score=council_res.confidence.final_score,
            retrieval_quality=council_res.confidence.retrieval_quality,
            evidence_coverage=council_res.confidence.evidence_coverage,
            agent_agreement=council_res.confidence.agent_agreement,
            weights_used=council_res.confidence.weights_used,
            commit=False,
        )

        all_agent_schemas = list(council_res.agent_responses)
        critique_schema = AgentResponseSchema(
            agent_name="challenger",
            answer=council_res.challenge_critique.critique_summary,
            key_points={
                "weaknesses": council_res.challenge_critique.weaknesses,
                "unsupported_claims": council_res.challenge_critique.unsupported_claims,
                "missing_considerations": council_res.challenge_critique.missing_considerations,
            },
            self_reported_confidence=0.0,
            latency_ms=0.0,
        )
        all_agent_schemas.append(critique_schema)

        for r in all_agent_schemas:
            logger.info(
                f"[Diagnostic ChatService] agent_name='{r.agent_name}', "
                f"answer_present={bool(r.answer and r.answer.strip())}, "
                f"answer_length={len(r.answer)}, "
                f"error={r.error}, "
                f"parsed_confidence={r.self_reported_confidence}"
            )

        await agent_repo.create_batch(
            message_id=assistant_msg.id,
            responses=all_agent_schemas,
            commit=False,
        )

        await agent_repo.create_evidence_batch(
            message_id=assistant_msg.id,
            chunk_refs=council_res.retrieved_chunks,
            commit=False,
        )

        await db.commit()
        await db.refresh(assistant_msg)
        logger.info(
            f"Atomically saved assistant reply {assistant_msg.id} with {len(all_agent_schemas)} agent rows and {len(council_res.retrieved_chunks)} evidence links."
        )
    except Exception as exc:
        await db.rollback()
        logger.error(
            f"Database persistence failed during atomic save for chat {chat_id}: {exc}",
            exc_info=True,
        )
        await msg_repo.update_status(user_msg, status="failed", commit=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save assistant response atomically.",
        )

    # 7. Return complete structured MessageResponse
    detailed_msg = await msg_repo.get_by_id_with_details(assistant_msg.id)
    if not detailed_msg:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve persisted message details.",
        )
    return MessageResponse.model_validate(detailed_msg)


async def list_chats(db: AsyncSession, user: User) -> List[ChatSummary]:
    """List all chat sessions owned by the user."""
    repo = ChatRepository(db)
    chats = await repo.list_by_user(user_id=user.id)
    return [ChatSummary.model_validate(c) for c in chats]


async def get_chat_detail(
    db: AsyncSession, user: User, chat_id: uuid.UUID | str
) -> ChatDetail:
    """Get full details of a chat session including all chronological messages and evaluations."""
    repo = ChatRepository(db)
    chat = await repo.get_detail_by_id_for_user(chat_id=chat_id, user_id=user.id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found or access denied.",
        )
    return ChatDetail.model_validate(chat)


async def delete_chat(db: AsyncSession, user: User, chat_id: uuid.UUID | str) -> bool:
    """Delete a chat session and cascade delete all its messages and evaluation artifacts."""
    repo = ChatRepository(db)
    chat = await repo.get_by_id_for_user(chat_id=chat_id, user_id=user.id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found or access denied.",
        )
    await repo.delete(chat)
    logger.info(
        f"Deleted chat {chat_id} and all associated artifacts for user {user.id}"
    )
    return True
