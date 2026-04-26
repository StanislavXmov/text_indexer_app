from dataclasses import dataclass


@dataclass(frozen=True)
class RAGConfig:
    chroma_path: str = "./chroma_db_0"
    collection_name: str = "guide"
    collection_description: str = "Guide"
    embedding_model_name: str = "multi-qa-mpnet-base-dot-v1"
    llm_model_name: str = "qwen2.5:0.5b"
    llm_temperature: float = 0.1
    llm_timeout_seconds: float = 75.0
    llm_num_predict: int = 256
    default_n_results: int = 5
    max_context_chars: int = 2000
    output_pdf_path: str = "output0.pdf"
    font_path: str = "../static/Roboto-Regular.ttf"
    font_name: str = "Roboto-Regular"
