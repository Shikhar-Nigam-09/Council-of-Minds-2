import uuid
from typing import Annotated, Dict, List

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.document import (
    DocumentRenameRequest,
    DocumentResponse,
    PaginatedChunksResponse,
)
from app.services.document_service import DocumentService
from app.services.storage.cloudinary_client import CloudinaryStorageClient
from app.workers.ingestion_worker import background_ingest_document
from app.workers.stuck_document_detector import find_and_reprocess_stuck_documents

router = APIRouter()


def get_document_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DocumentService:
    """Dependency injection for DocumentService with Cloudinary storage client."""
    return DocumentService(db, CloudinaryStorageClient())


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new document (PDF/TXT/MD)",
)
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
):
    """Upload a PDF, TXT, or Markdown document to Cloudinary and trigger RAG ingestion."""
    return await service.upload_document(current_user, file, background_tasks)


@router.get(
    "",
    response_model=List[DocumentResponse],
    status_code=status.HTTP_200_OK,
    summary="List all documents owned by user",
)
async def list_documents(
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all uploaded documents owned by the currently authenticated user."""
    # Opportunistically check and reprocess any stuck background ingestion tasks
    await find_and_reprocess_stuck_documents(db, background_tasks)
    return await service.list_user_documents(current_user)


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document details by ID",
)
async def get_document(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
):
    """Get specific document metadata if owned by the authenticated user."""
    return await service.get_user_document(current_user, document_id)


@router.get(
    "/{document_id}/chunks",
    response_model=PaginatedChunksResponse,
    status_code=status.HTTP_200_OK,
    summary="Get paginated document chunks",
)
async def get_document_chunks(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = 1,
    page_size: int = 20,
):
    """Get paginated chunks for a document owned by the authenticated user."""
    await service.get_user_document(current_user, document_id)
    from app.repositories.chunk_repository import ChunkRepository

    chunk_repo = ChunkRepository(db)
    chunks, total = await chunk_repo.list_by_document_id_paginated(
        document_id=document_id, page=page, page_size=page_size
    )
    return {
        "chunks": chunks,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.patch(
    "/{document_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Rename document filename",
)
async def rename_document(
    document_id: uuid.UUID,
    request: DocumentRenameRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
):
    """Rename original filename of a document owned by the authenticated user."""
    return await service.rename_document(
        current_user, document_id, request.new_filename
    )


@router.post(
    "/{document_id}/retry",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Retry processing or deletion for a failed/stuck document",
)
async def retry_document(
    document_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
):
    """Resubmit a failed, deletion_failed, or stuck document to background ingestion or deletion retry."""
    doc = await service.get_user_document(current_user, document_id)

    if doc.status == "deletion_failed":
        await service.delete_document(current_user, document_id)
        doc.status = "deleted"
        return doc

    doc.status = "uploaded"
    doc.processing_error = None
    await service.db.commit()
    await service.db.refresh(doc)

    background_tasks.add_task(background_ingest_document, doc.id, force=True)
    return doc


@router.delete(
    "/{document_id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Delete document and Cloudinary asset",
)
async def delete_document(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
):
    """Delete document from Cloudinary storage, FAISS index, and database."""
    await service.delete_document(current_user, document_id)
    return {"status": "success", "message": "Document deleted successfully."}
