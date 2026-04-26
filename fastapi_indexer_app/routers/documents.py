from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status

from fastapi_indexer_app.db import DocumentRepository
from fastapi_indexer_app.schemas import DocumentIndexResponse
from fastapi_indexer_app.services.ingestion import build_chroma_path, run_uploaded_pdf_indexing

router = APIRouter(prefix="/documents", tags=["documents"])
repository = DocumentRepository()

UPLOAD_DIR = Path("documents") / "uploaded"
CHROMA_BASE_DIR = Path("data") / "chroma" / "uploaded"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_BASE_DIR.mkdir(parents=True, exist_ok=True)


def _read_response(document_id: UUID) -> DocumentIndexResponse:
    row = repository.get_document(document_id)
    return _row_to_response(row)


def _row_to_response(row: tuple) -> DocumentIndexResponse:
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


def _process_indexing_job(*, document_id: UUID, stored_filename: str, collection_name: str) -> None:
    repository.update_processing(document_id)
    chroma_path = build_chroma_path(
        filename=stored_filename,
        base_path=str(CHROMA_BASE_DIR),
        document_id=str(document_id),
    )
    try:
        indexed_chunks = run_uploaded_pdf_indexing(
            output_folder=str(UPLOAD_DIR),
            stored_filename=stored_filename,
            chroma_path=chroma_path,
            collection_name=collection_name,
        )
        repository.update_completed(document_id, chroma_path=chroma_path, indexed_chunks=indexed_chunks)
    except Exception as exc:
        repository.update_failed(document_id, error_message=str(exc))


@router.get("", response_model=list[DocumentIndexResponse])
def list_documents() -> list[DocumentIndexResponse]:
    rows = repository.list_documents()
    return [_row_to_response(row) for row in rows]


@router.get("/{document_id}", response_model=DocumentIndexResponse)
def get_document(document_id: UUID) -> DocumentIndexResponse:
    try:
        return _read_response(document_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("/index", response_model=DocumentIndexResponse, status_code=status.HTTP_201_CREATED)
async def index_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)) -> DocumentIndexResponse:
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

    # Persist upload first, then index and update processing status.
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    repository.create_pending_document(
        original_filename=original_name,
        stored_filename=stored_filename,
        stored_path=str(stored_path),
        collection_name=f"doc_{str(document_id).replace('-', '')[:12]}",
        document_id=document_id,
    )

    stored_path.write_bytes(file_bytes)

    collection_name = f"doc_{str(document_id).replace('-', '')[:12]}"
    background_tasks.add_task(
        _process_indexing_job,
        document_id=document_id,
        stored_filename=stored_filename,
        collection_name=collection_name,
    )
    return _read_response(document_id)
