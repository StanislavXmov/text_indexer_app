from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from set_documents.chunking import create_text_splitter, split_document
from set_documents.config import DocumentIngestionConfig
from set_documents.indexer import index_chunks
from set_documents.reader import load_document_content


def sanitize_for_path(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-") or "document"


def build_chroma_path(filename: str, base_path: str, document_id: str) -> str:
    stem = sanitize_for_path(Path(filename).stem)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = document_id.replace("-", "")[:8]
    return str(Path(base_path) / f"{stem}_{timestamp}_{suffix}")


def run_uploaded_pdf_indexing(
    *,
    output_folder: str,
    stored_filename: str,
    chroma_path: str,
    collection_name: str,
) -> int:
    config = DocumentIngestionConfig()
    _, content = load_document_content(output_folder, stored_filename)
    splitter = create_text_splitter(config.chunk_size, config.chunk_overlap)
    file_path = Path(output_folder) / stored_filename
    chunks = split_document(content, file_path, splitter)

    return index_chunks(
        chunks=chunks,
        chroma_path=chroma_path,
        collection_name=collection_name,
        collection_description=f"Indexed document {stored_filename}",
        embedding_model_name=config.embedding_model_name,
    )
