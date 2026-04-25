from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_text_splitter(chunk_size: int, chunk_overlap: int) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def split_document(content: str, source: Path, text_splitter: RecursiveCharacterTextSplitter) -> list[dict]:
    chunks = text_splitter.split_text(content)
    return [{"content": chunk, "source": source} for chunk in chunks]
