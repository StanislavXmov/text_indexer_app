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
