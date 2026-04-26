from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import chromadb
from fastapi import HTTPException, UploadFile, status

from fastapi_indexer_app.db import DocumentRepository
from fastapi_indexer_app.schemas import DocumentIndexDebugResponse, DocumentIndexResponse
from fastapi_indexer_app.services.ingestion import build_chroma_path, run_uploaded_pdf_indexing

UPLOAD_DIR = Path("documents") / "uploaded"
CHROMA_BASE_DIR = Path("data") / "chroma" / "uploaded"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_BASE_DIR.mkdir(parents=True, exist_ok=True)


class DocumentsService:
    def __init__(self, repository: DocumentRepository) -> None:
        self._repository = repository

    def row_to_response(self, row: tuple) -> DocumentIndexResponse:
        return DocumentIndexResponse(
            document_id=row[0],
            original_filename=row[1],
            stored_filename=row[2],
            status=row[3],
            collection_name=row[4],
            chroma_path=row[5],
            indexed_chunks=row[6],
            created_at=row[7],
            updated_at=row[8],
        )

    def get_document_response(self, document_id: UUID) -> DocumentIndexResponse:
        row = self._repository.get_document(document_id)
        return self.row_to_response(row)

    def list_document_responses(self) -> list[DocumentIndexResponse]:
        rows = self._repository.list_documents()
        return [self.row_to_response(row) for row in rows]

    def get_index_debug(self, document_id: UUID) -> DocumentIndexDebugResponse:
        document = self.get_document_response(document_id)
        if document.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document is not indexed yet. Wait until status becomes completed.",
            )

        try:
            client = chromadb.PersistentClient(path=document.chroma_path)
            collection = client.get_collection(name=document.collection_name)
            collection_count = collection.count()
            sample_result = collection.get(limit=2, include=["documents"])
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unable to read index debug info: {exc}",
            ) from exc

        raw_documents = sample_result.get("documents", [])
        sample_chunks = [item for item in raw_documents if isinstance(item, str)]
        if sample_chunks and len(sample_chunks) == 1 and sample_chunks[0] == "":
            sample_chunks = []

        return DocumentIndexDebugResponse(
            document_id=document.document_id,
            status=document.status,
            chroma_path=document.chroma_path,
            collection_name=document.collection_name,
            indexed_chunks=document.indexed_chunks,
            collection_count=collection_count,
            sample_chunks=sample_chunks[:2],
        )

    async def prepare_index_job(self, file: UploadFile) -> tuple[UUID, DocumentIndexResponse]:
        filename = file.filename or ""
        is_pdf = filename.lower().endswith(".pdf") or file.content_type == "application/pdf"
        if not is_pdf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported.",
            )

        original_name = Path(filename).name
        file_suffix = Path(original_name).suffix.lower() or ".pdf"
        base_name = Path(original_name).stem.replace(" ", "_") or "document"
        document_id = uuid4()
        stored_filename = f"{base_name}_{str(document_id).replace('-', '')[:8]}{file_suffix}"
        stored_path = UPLOAD_DIR / stored_filename

        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

        self._repository.create_pending_document(
            original_filename=original_name,
            stored_filename=stored_filename,
            stored_path=str(stored_path),
            collection_name=f"doc_{str(document_id).replace('-', '')[:12]}",
            document_id=document_id,
        )
        stored_path.write_bytes(file_bytes)
        return document_id, self.get_document_response(document_id)

    def process_indexing_job(self, *, document_id: UUID) -> None:
        document = self.get_document_response(document_id)
        self._repository.update_processing(document_id)
        chroma_path = build_chroma_path(
            filename=document.stored_filename,
            base_path=str(CHROMA_BASE_DIR),
            document_id=str(document_id),
        )
        try:
            indexed_chunks = run_uploaded_pdf_indexing(
                output_folder=str(UPLOAD_DIR),
                stored_filename=document.stored_filename,
                chroma_path=chroma_path,
                collection_name=document.collection_name,
            )
            self._repository.update_completed(document_id, chroma_path=chroma_path, indexed_chunks=indexed_chunks)
        except Exception as exc:
            self._repository.update_failed(document_id, error_message=str(exc))
