from typing import List, Tuple

import chromadb
from sentence_transformers import SentenceTransformer

from get_answer.config import RAGConfig


class Retriever:
    def __init__(self, config: RAGConfig) -> None:
        self._config = config
        self._client = chromadb.PersistentClient(path=config.chroma_path)
        self._collection = self._client.get_or_create_collection(
            name=config.collection_name,
            metadata={"description": config.collection_description},
        )
        self._embedding_model = SentenceTransformer(config.embedding_model_name)

    def retrieve_context(self, question: str, n_results: int | None = None) -> Tuple[str, List[str]]:
        if not question.strip():
            return "", []

        if n_results is None:
            effective_n_results = self._config.default_n_results
        elif not isinstance(n_results, int) or n_results <= 0:
            raise ValueError("n_results must be a positive integer.")
        else:
            effective_n_results = n_results

        query_embedding = self._embedding_model.encode([question])
        results = self._collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=effective_n_results,
            include=["documents"],
        )

        documents_batches = results.get("documents", [])
        if not documents_batches or not documents_batches[0]:
            return "", []

        documents = documents_batches[0]
        context = "\n\n---SECTION---\n\n".join(documents)
        return context, documents
