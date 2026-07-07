import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    """Schema for returning document metadata."""

    id: uuid.UUID
    user_id: uuid.UUID
    original_filename: str
    cloudinary_public_id: str
    cloudinary_url: str
    file_type: str
    file_size_bytes: int
    status: str
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentRenameRequest(BaseModel):
    """Request schema for renaming a document."""

    new_filename: str


class DocumentChunkResponse(BaseModel):
    """Schema for returning document chunk details."""

    id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int
    content: str
    faiss_vector_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedChunksResponse(BaseModel):
    """Schema for returning paginated document chunks."""

    chunks: list[DocumentChunkResponse]
    total: int
    page: int
    page_size: int
