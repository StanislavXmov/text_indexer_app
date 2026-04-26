from fastapi import FastAPI

from fastapi_indexer_app.routers.documents import router as documents_router

app = FastAPI(title="Document Indexing API")
app.include_router(documents_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
