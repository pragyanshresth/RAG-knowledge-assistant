from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class DocumentOut(BaseModel):
    id: str
    filename: str
    file_type: str
    uploaded_at: datetime
    status: str
    source_path: str
    metadata: dict = {}


class IndexRequest(BaseModel):
    document_ids: list[str] | None = None  # None = (re)index everything


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    top_k: int | None = Field(default=None, ge=1, le=20)


class Source(BaseModel):
    document: str
    section: str
    score: float


class RetrievedChunk(BaseModel):
    document: str
    section: str
    chunk_index: int
    text: str
    score: float


class QueryResult(BaseModel):
    answer: str
    sources: list[Source]
    retrieved_chunks: list[RetrievedChunk]
    confidence: Literal["high", "medium", "low", "none"]
    follow_up_questions: list[str] = []
