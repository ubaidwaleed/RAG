from fastapi import FastAPI
from pydantic import BaseModel

from agent.agent import answer_query
from config import settings

app = FastAPI(title=settings.app_name)


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    answer = answer_query(request.query)
    return QueryResponse(answer=answer)
