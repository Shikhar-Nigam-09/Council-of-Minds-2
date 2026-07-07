import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.models.user import User
from app.schemas.chat import ChatDetail, ChatSummary
from app.schemas.message import MessageResponse, SendMessageRequest
from app.services import chat_service

router = APIRouter()


@router.post(
    "/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ask a question and receive a synthesized answer from the Council of Minds",
)
@limiter.limit(settings.RATE_LIMIT_QUESTIONS_PER_MINUTE)
async def ask_question_endpoint(
    request: Request,
    payload: SendMessageRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Submits a question to the Council of Minds.
    - Creates a new chat session if `chat_id` is None.
    - Incorporates bounded recent conversation history and composes a Contextual Retrieval Query.
    - Evaluates across 5 reasoning personas and Challenger critique.
    - Atomically persists user question, assistant reply, agent evaluations, and document evidence.
    """
    return await chat_service.ask_question(
        db=db,
        user=current_user,
        question=payload.question,
        chat_id=payload.chat_id,
    )


@router.get(
    "",
    response_model=List[ChatSummary],
    status_code=status.HTTP_200_OK,
    summary="List all chat sessions for the current user",
)
async def list_chats_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all chat sessions owned by the authenticated user, ordered by last activity."""
    return await chat_service.list_chats(db=db, user=current_user)


@router.get(
    "/{chat_id}",
    response_model=ChatDetail,
    status_code=status.HTTP_200_OK,
    summary="Get detailed chat history and evaluation breakdown",
)
async def get_chat_detail_endpoint(
    chat_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Fetch full chat session details including chronological messages, persona evaluations, and evidence links."""
    return await chat_service.get_chat_detail(db=db, user=current_user, chat_id=chat_id)


@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a chat session",
)
async def delete_chat_endpoint(
    chat_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a chat session and cascade delete all associated messages, agent responses, and evidence."""
    await chat_service.delete_chat(db=db, user=current_user, chat_id=chat_id)
