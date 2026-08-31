import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from agent.agent import answer_query
from config import settings
from ingest.ingest import upsert_document
from ingest.parsers import extract_text

MAX_UPLOAD_BYTES = settings.max_upload_size_mb * 1024 * 1024

app = FastAPI(title=settings.app_name)


class QueryRequest(BaseModel):
    query: str
    document_id: str | None = None


class QueryResponse(BaseModel):
    answer: str


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunk_count: int


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    answer = answer_query(request.query, namespace=request.document_id or "")
    return QueryResponse(answer=answer)


@app.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)) -> UploadResponse:
    content = await file.read()

    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=400, detail=f"File too large (max {settings.max_upload_size_mb} MB)"
        )

    try:
        text = extract_text(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not text.strip():
        raise HTTPException(status_code=400, detail="No extractable text found in file")

    document_id = uuid.uuid4().hex[:12]
    chunk_count = upsert_document(file.filename, text, namespace=document_id)

    return UploadResponse(document_id=document_id, filename=file.filename, chunk_count=chunk_count)
