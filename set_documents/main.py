from set_documents.chunking import create_text_splitter, split_document
from set_documents.config import DocumentIngestionConfig
from set_documents.indexer import index_chunks
from set_documents.reader import load_document_content


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
    config = DocumentIngestionConfig()
    count = run_ingestion(config)
    print(f"Collection count: {count}")


if __name__ == "__main__":
    main()
