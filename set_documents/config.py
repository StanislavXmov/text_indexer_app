from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentIngestionConfig:
    output_folder: str = "documents"
    filename: str = "Регламент работы ЭТП Фабрикант по капитальному ремонту МКД.pdf"
    chroma_path: str = "./data/chroma/set_documents"
    collection_name: str = "guide"
    collection_description: str = "Guide"
    chunk_size: int = 600
    chunk_overlap: int = 120
    embedding_model_name: str = "multi-qa-mpnet-base-dot-v1"
