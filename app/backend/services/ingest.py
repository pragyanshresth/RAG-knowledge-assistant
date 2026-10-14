import asyncio
import uuid
from backend.core.config import settings
from backend.models.db import Chunk, Document, SessionLocal
from backend.services import vectorstore
from backend.services.chunking import chunk_text
from backend.services.embeddings import embed
from backend.services.parsing import parse


async def index_document(doc_id: str) -> Document:
    """(Re)index one document: parse -> chunk -> embed -> store. Safe to call repeatedly."""
    with SessionLocal() as s:
        doc = s.get(Document, doc_id)
        try:
            segments = await asyncio.to_thread(parse, doc.source_path)
            rows, i = [], 0
            for section, text in segments:
                for piece in chunk_text(text, settings.chunk_size, settings.chunk_overlap):
                    rows.append(Chunk(id=str(uuid.uuid4()), document_id=doc.id, chunk_text=piece,
                                      chunk_index=i, section=section))
                    i += 1
            if not rows:
                raise ValueError("No extractable text found in document")
            vectors = await embed([r.chunk_text for r in rows])
            await vectorstore.delete_document(doc.id)
            doc.chunks.clear()
            s.flush()
            s.add_all(rows)
            await vectorstore.upsert([r.id for r in rows], vectors, [
                {"document_id": doc.id, "document": doc.filename, "section": r.section,
                 "chunk_index": r.chunk_index, "text": r.chunk_text} for r in rows])
            doc.status, doc.meta = "indexed", {**doc.meta, "chunks": len(rows), "error": None}
        except Exception as e:  # keep the failure visible in the UI
            doc.status, doc.meta = "failed", {**doc.meta, "error": str(e)}
        s.commit()
        return doc
