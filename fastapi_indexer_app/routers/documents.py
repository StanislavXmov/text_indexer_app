from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status

from fastapi_indexer_app.db import DocumentRepository
from fastapi_indexer_app.schemas import (
    DocumentIndexDebugResponse,
    DocumentIndexResponse,
    DocumentQuestionJobDetailResponse,
    DocumentQuestionJobResponse,
    DocumentQuestionRequest,
)
from fastapi_indexer_app.services.documents_service import DocumentsService
from fastapi_indexer_app.services.question_jobs_service import QuestionJobsService

router = APIRouter(prefix="/documents", tags=["documents"])
repository = DocumentRepository()
documents_service = DocumentsService(repository)
question_jobs_service = QuestionJobsService(repository, documents_service)


@router.get("", response_model=list[DocumentIndexResponse])
def list_documents() -> list[DocumentIndexResponse]:
    return documents_service.list_document_responses()


@router.get("/{document_id}", response_model=DocumentIndexResponse)
def get_document(document_id: UUID) -> DocumentIndexResponse:
    try:
        return documents_service.get_document_response(document_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get("/{document_id}/index-debug", response_model=DocumentIndexDebugResponse)
def get_document_index_debug(document_id: UUID) -> DocumentIndexDebugResponse:
    try:
        return documents_service.get_index_debug(document_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("/{document_id}/ask", response_model=DocumentQuestionJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def ask_document_question(
    document_id: UUID,
    payload: DocumentQuestionRequest,
    background_tasks: BackgroundTasks,
) -> DocumentQuestionJobResponse:
    job = question_jobs_service.create_job(document_id, payload)
    job_id = job.job_id
    background_tasks.add_task(
        question_jobs_service.process_job,
        job_id=job_id,
        document_id=document_id,
    )
    return job


@router.get("/ask-jobs/{job_id}", response_model=DocumentQuestionJobDetailResponse)
def get_question_job(job_id: UUID) -> DocumentQuestionJobDetailResponse:
    try:
        return question_jobs_service.get_job_response(job_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get("/{document_id}/ask-jobs/{job_id}", response_model=DocumentQuestionJobDetailResponse)
def get_document_question_job(document_id: UUID, job_id: UUID) -> DocumentQuestionJobDetailResponse:
    try:
        job = question_jobs_service.get_job_response(job_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    if job.document_id != document_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question job with id={job_id} is not found for document id={document_id}",
        )
    return job


@router.post("/index", response_model=DocumentIndexResponse, status_code=status.HTTP_201_CREATED)
async def index_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)) -> DocumentIndexResponse:
    document_id, document_response = await documents_service.prepare_index_job(file)
    background_tasks.add_task(
        documents_service.process_indexing_job,
        document_id=document_id,
    )
    return document_response
