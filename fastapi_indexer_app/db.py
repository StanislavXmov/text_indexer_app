from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

import duckdb


class DocumentRepository:
    def __init__(self, db_path: str = "data/documents.duckdb") -> None:
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    def _connect(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(self.db_path)

    def _initialize_schema(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS indexed_documents (
                    id UUID PRIMARY KEY,
                    original_filename VARCHAR NOT NULL,
                    stored_filename VARCHAR NOT NULL,
                    stored_path VARCHAR NOT NULL,
                    collection_name VARCHAR NOT NULL,
                    chroma_path VARCHAR,
                    status VARCHAR NOT NULL,
                    indexed_chunks INTEGER,
                    error_message VARCHAR,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                );
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS question_jobs (
                    id UUID PRIMARY KEY,
                    document_id UUID NOT NULL,
                    question VARCHAR NOT NULL,
                    n_results INTEGER,
                    status VARCHAR NOT NULL,
                    answer VARCHAR,
                    error_message VARCHAR,
                    started_at TIMESTAMP,
                    finished_at TIMESTAMP,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                );
                """
            )
            con.execute("ALTER TABLE question_jobs ADD COLUMN IF NOT EXISTS started_at TIMESTAMP;")
            con.execute("ALTER TABLE question_jobs ADD COLUMN IF NOT EXISTS finished_at TIMESTAMP;")

    def create_pending_document(
        self,
        *,
        original_filename: str,
        stored_filename: str,
        stored_path: str,
        collection_name: str,
        document_id: UUID | None = None,
    ) -> UUID:
        document_id = document_id or uuid4()
        now = datetime.now(UTC)
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO indexed_documents (
                    id,
                    original_filename,
                    stored_filename,
                    stored_path,
                    collection_name,
                    status,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
                """,
                [
                    document_id,
                    original_filename,
                    stored_filename,
                    stored_path,
                    collection_name,
                    now,
                    now,
                ],
            )
        return document_id

    def update_processing(self, document_id: UUID) -> None:
        with self._connect() as con:
            con.execute(
                """
                UPDATE indexed_documents
                SET status = 'processing', updated_at = ?
                WHERE id = ?
                """,
                [datetime.now(UTC), document_id],
            )

    def update_completed(self, document_id: UUID, *, chroma_path: str, indexed_chunks: int) -> None:
        with self._connect() as con:
            con.execute(
                """
                UPDATE indexed_documents
                SET status = 'completed',
                    chroma_path = ?,
                    indexed_chunks = ?,
                    error_message = NULL,
                    updated_at = ?
                WHERE id = ?
                """,
                [chroma_path, indexed_chunks, datetime.now(UTC), document_id],
            )

    def update_failed(self, document_id: UUID, *, error_message: str) -> None:
        with self._connect() as con:
            con.execute(
                """
                UPDATE indexed_documents
                SET status = 'failed',
                    error_message = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                [error_message, datetime.now(UTC), document_id],
            )

    def get_document(self, document_id: UUID) -> tuple:
        with self._connect() as con:
            row = con.execute(
                """
                SELECT
                    id,
                    original_filename,
                    stored_filename,
                    status,
                    collection_name,
                    COALESCE(chroma_path, ''),
                    COALESCE(indexed_chunks, 0),
                    created_at,
                    updated_at
                FROM indexed_documents
                WHERE id = ?
                """,
                [document_id],
            ).fetchone()
        if row is None:
            raise ValueError(f"Document with id={document_id} not found")
        return row

    def list_documents(self) -> list[tuple]:
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT
                    id,
                    original_filename,
                    stored_filename,
                    status,
                    collection_name,
                    COALESCE(chroma_path, ''),
                    COALESCE(indexed_chunks, 0),
                    created_at,
                    updated_at
                FROM indexed_documents
                ORDER BY created_at DESC
                """
            ).fetchall()
        return rows

    def create_question_job(
        self,
        *,
        document_id: UUID,
        question: str,
        n_results: int | None,
    ) -> UUID:
        job_id = uuid4()
        now = datetime.now(UTC)
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO question_jobs (
                    id,
                    document_id,
                    question,
                    n_results,
                    status,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, 'pending', ?, ?)
                """,
                [job_id, document_id, question, n_results, now, now],
            )
        return job_id

    def update_question_job_processing(self, job_id: UUID) -> None:
        with self._connect() as con:
            con.execute(
                """
                UPDATE question_jobs
                SET status = 'processing',
                    started_at = COALESCE(started_at, ?),
                    updated_at = ?
                WHERE id = ?
                """,
                [datetime.now(UTC), datetime.now(UTC), job_id],
            )

    def update_question_job_completed(self, job_id: UUID, *, answer: str) -> None:
        with self._connect() as con:
            con.execute(
                """
                UPDATE question_jobs
                SET status = 'completed',
                    answer = ?,
                    error_message = NULL,
                    finished_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                [answer, datetime.now(UTC), datetime.now(UTC), job_id],
            )

    def update_question_job_failed(self, job_id: UUID, *, error_message: str) -> None:
        with self._connect() as con:
            con.execute(
                """
                UPDATE question_jobs
                SET status = 'failed',
                    error_message = ?,
                    finished_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                [error_message, datetime.now(UTC), datetime.now(UTC), job_id],
            )

    def get_question_job(self, job_id: UUID) -> tuple:
        with self._connect() as con:
            row = con.execute(
                """
                SELECT
                    id,
                    document_id,
                    question,
                    status,
                    answer,
                    error_message,
                    started_at,
                    finished_at,
                    created_at,
                    updated_at,
                    n_results
                FROM question_jobs
                WHERE id = ?
                """,
                [job_id],
            ).fetchone()
        if row is None:
            raise ValueError(f"Question job with id={job_id} not found")
        return row

    def clear_database(self) -> None:
        with self._connect() as con:
            con.execute("BEGIN TRANSACTION;")
            con.execute("DELETE FROM question_jobs;")
            con.execute("DELETE FROM indexed_documents;")
            con.execute("COMMIT;")
