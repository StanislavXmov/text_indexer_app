import argparse
import re
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from set_documents.chunking import create_text_splitter, split_document
from set_documents.config import DocumentIngestionConfig
from set_documents.indexer import index_chunks
from set_documents.reader import load_document_content


def _sanitize_for_path(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-") or "document"


def _build_chroma_path(filename: str, chroma_base_path: str) -> str:
    stem = _sanitize_for_path(Path(filename).stem)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(Path(chroma_base_path) / f"{stem}_{timestamp}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Index a document into ChromaDB.")
    parser.add_argument(
        "--filename",
        type=str,
        help="Document file name from the documents folder (for example: book.pdf).",
    )
    parser.add_argument(
        "--chroma-path",
        type=str,
        help="Base directory for Chroma DB. A new subfolder is created per file.",
    )
    return parser.parse_args()


def run_ingestion(config: DocumentIngestionConfig) -> int:
    file_path, content = load_document_content(config.output_folder, config.filename)
    splitter = create_text_splitter(config.chunk_size, config.chunk_overlap)
    chunks = split_document(content, file_path, splitter)

    return index_chunks(
        chunks=chunks,
        chroma_path=config.chroma_path,
        collection_name=config.collection_name,
        collection_description=config.collection_description,
        embedding_model_name=config.embedding_model_name,
    )


def main() -> None:
    args = _parse_args()
    config = DocumentIngestionConfig()
    filename = args.filename or config.filename
    chroma_base_path = args.chroma_path or config.chroma_path
    chroma_path = _build_chroma_path(filename, chroma_base_path)
    runtime_config = replace(config, filename=filename, chroma_path=chroma_path)

    print(f"Indexing file: {filename}")
    print(f"Chroma path: {chroma_path}")
    count = run_ingestion(runtime_config)
    print(f"Collection count: {count}")


if __name__ == "__main__":
    main()
