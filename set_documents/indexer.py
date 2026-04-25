from pathlib import Path
from functools import lru_cache

import chromadb
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=None)
def get_embedding_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)


def index_chunks(
    chunks: list[dict],
    chroma_path: str,
    collection_name: str,
    collection_description: str,
    embedding_model_name: str,
) -> int:
    Path(chroma_path).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"description": collection_description},
    )

    model = get_embedding_model(embedding_model_name)
    documents = [chunk["content"] for chunk in chunks]
    embeddings = model.encode(documents)
    metadatas = [{"document": Path(chunk["source"]).name} for chunk in chunks]
    ids = [f"doc_{index}" for index in range(len(documents))]

    collection.add(
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
        ids=ids,
    )
    return collection.count()
