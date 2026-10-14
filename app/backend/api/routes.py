import re
import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile
from backend.core.config import settings
from backend.models.db import Document, SessionLocal
from backend.schemas.schemas import DocumentOut, IndexRequest, QueryRequest, QueryResult
from backend.services import ingest, rag
from backend.services.parsing import SUPPORTED

router = APIRouter()


def _out(d: Document) -> DocumentOut:
    return DocumentOut(id=d.id, filename=d.filename, file_type=d.file_type, uploaded_at=d.uploaded_at,
                       status=d.status, source_path=d.source_path, metadata=d.meta or {})


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/documents/upload", response_model=DocumentOut, status_code=201)
async def upload(file: UploadFile):
    name = re.sub(r"[^\w.\- ]", "_", Path(file.filename or "").name)
    ext = Path(name).suffix.lower()
    if ext not in SUPPORTED:
        raise HTTPException(415, f"Unsupported file type '{ext}'. Allowed: {sorted(SUPPORTED)}")
    dest = Path(settings.upload_dir)
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"{uuid.uuid4().hex[:8]}-{name}"
    with path.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    size = path.stat().st_size
    if size == 0 or size > settings.max_upload_mb * 1024 * 1024:
        path.unlink()
        raise HTTPException(413 if size else 400, "File is empty or exceeds the size limit")
    with SessionLocal() as s:
        doc = Document(filename=name, file_type=ext[1:], source_path=str(path), meta={"size_bytes": size})
        s.add(doc)
        s.commit()
        return _out(doc)


@router.post("/documents/index", response_model=list[DocumentOut])
async def index(req: IndexRequest):
    with SessionLocal() as s:
        ids = req.document_ids or [d.id for d in s.query(Document).all()]
        missing = [i for i in ids if not s.get(Document, i)]
    if missing:
        raise HTTPException(404, f"Unknown document ids: {missing}")
    return [_out(await ingest.index_document(i)) for i in ids]


@router.get("/documents", response_model=list[DocumentOut])
async def list_documents():
    with SessionLocal() as s:
        return [_out(d) for d in s.query(Document).order_by(Document.uploaded_at.desc())]


@router.post("/query", response_model=QueryResult)
async def query(req: QueryRequest):
    try:
        return await rag.answer_question(req.question, req.top_k)
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(502, f"Upstream model error: {e}")
