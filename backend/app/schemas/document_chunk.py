import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentChunkBase(BaseModel):
    chunk_index: int
    content: str
    faiss_vector_id: str


class DocumentChunkCreate(DocumentChunkBase):
    document_id: uuid.UUID
    user_id: uuid.UUID


class DocumentChunkResponse(DocumentChunkBase):
    id: uuid.UUID
    document_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
