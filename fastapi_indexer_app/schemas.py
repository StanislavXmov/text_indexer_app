from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentIndexResponse(BaseModel):
    document_id: UUID
    original_filename: str
    stored_filename: str
    status: str
    collection_name: str
    chroma_path: str
    indexed_chunks: int
    created_at: datetime
    updated_at: datetime


class DocumentIndexDebugResponse(BaseModel):
    document_id: UUID
    status: str
    chroma_path: str
    collection_name: str
    indexed_chunks: int
    collection_count: int
    sample_chunks: list[str]


class DocumentQuestionRequest(BaseModel):
    question: str
    n_results: int | None = None


class DocumentQuestionJobResponse(BaseModel):
    job_id: UUID
    document_id: UUID
    question: str
    status: str
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class DocumentQuestionJobDetailResponse(BaseModel):
    job_id: UUID
    document_id: UUID
    question: str
    status: str
    answer: str | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
