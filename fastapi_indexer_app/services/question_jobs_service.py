from __future__ import annotations

import asyncio
from dataclasses import replace
from datetime import datetime, timedelta
from functools import lru_cache
from uuid import UUID

from fastapi import HTTPException, status

from fastapi_indexer_app.db import DocumentRepository
from fastapi_indexer_app.schemas import (
    DocumentQuestionJobDetailResponse,
    DocumentQuestionJobResponse,
    DocumentQuestionRequest,
)
from fastapi_indexer_app.services.documents_service import DocumentsService
from get_answer.config import RAGConfig
from get_answer.pipeline import RAGPipeline

ASK_TIMEOUT_SECONDS = 90
STALE_JOB_GRACE_SECONDS = 30


class QuestionJobsService:
    def __init__(self, repository: DocumentRepository, documents_service: DocumentsService) -> None:
        self._repository = repository
        self._documents_service = documents_service

    def row_to_detail_response(self, row: tuple) -> DocumentQuestionJobDetailResponse:
        return DocumentQuestionJobDetailResponse(
            job_id=row[0],
            document_id=row[1],
            question=row[2],
            status=row[3],
            answer=row[4],
            error_message=row[5],
            started_at=row[6],
            finished_at=row[7],
            created_at=row[8],
            updated_at=row[9],
        )

    def get_job_response(self, job_id: UUID) -> DocumentQuestionJobDetailResponse:
        row = self._repository.get_question_job(job_id)
        row = self._recover_stale_processing_job(row)
        return self.row_to_detail_response(row)

    def create_job(self, document_id: UUID, payload: DocumentQuestionRequest) -> DocumentQuestionJobResponse:
        try:
            self._documents_service.get_document_response(document_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

        if not payload.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question must not be empty.",
            )

        job_id = self._repository.create_question_job(
            document_id=document_id,
            question=payload.question,
            n_results=payload.n_results,
        )
        job = self._repository.get_question_job(job_id)
        return DocumentQuestionJobResponse(
            job_id=job[0],
            document_id=job[1],
            question=job[2],
            status=job[3],
            started_at=job[6],
            finished_at=job[7],
            created_at=job[8],
            updated_at=job[9],
        )

    def process_job(self, *, job_id: UUID, document_id: UUID) -> None:
        self._repository.update_question_job_processing(job_id)
        try:
            answer = asyncio.run(
                asyncio.wait_for(
                    asyncio.to_thread(
                        self._build_answer,
                        job_id,
                        document_id,
                    ),
                    timeout=ASK_TIMEOUT_SECONDS,
                )
            )
            self._repository.update_question_job_completed(job_id, answer=answer)
        except TimeoutError:
            self._repository.update_question_job_failed(
                job_id,
                error_message="Answer generation timed out. Try smaller n_results or retry later.",
            )
        except Exception as exc:
            self._repository.update_question_job_failed(job_id, error_message=str(exc))

    def _build_answer(self, job_id: UUID, document_id: UUID) -> str:
        document = self._documents_service.get_document_response(document_id)
        if document.status != "completed":
            raise ValueError("Document is not indexed yet. Wait until status becomes completed.")

        job = self._repository.get_question_job(job_id)
        question = job[2]
        n_results = job[10]
        pipeline = self._get_pipeline(document.chroma_path, document.collection_name, document.stored_filename)
        return pipeline.enhanced_query_with_llm(question, n_results)

    def _recover_stale_processing_job(self, row: tuple) -> tuple:
        status = row[3]
        started_at = row[6]
        finished_at = row[7]
        if status != "processing" or started_at is None or finished_at is not None:
            return row

        # DB stores naive local timestamps; compare in the same naive scale.
        timeout_deadline = started_at + timedelta(
            seconds=ASK_TIMEOUT_SECONDS + STALE_JOB_GRACE_SECONDS
        )
        if datetime.now() <= timeout_deadline:
            return row

        self._repository.update_question_job_failed(
            row[0],
            error_message=(
                "Job was left in processing too long and marked as failed "
                "(likely interrupted by reload/restart)."
            ),
        )
        return self._repository.get_question_job(row[0])

    @staticmethod
    @lru_cache(maxsize=16)
    def _get_pipeline(chroma_path: str, collection_name: str, stored_filename: str) -> RAGPipeline:
        rag_config = replace(
            RAGConfig(),
            chroma_path=chroma_path,
            collection_name=collection_name,
            collection_description=f"Indexed document {stored_filename}",
        )
        return RAGPipeline(rag_config)
