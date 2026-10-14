"""Upload + index everything in data/sample_docs:  python -m backend.seed"""
import asyncio
from pathlib import Path
from backend.models.db import Document, SessionLocal, init_db
from backend.services.ingest import index_document


async def main():
    init_db()
    for p in sorted(Path("data/sample_docs").glob("*.md")):
        if p.name == "sample_queries.md":
            continue
        with SessionLocal() as s:
            if s.query(Document).filter_by(filename=p.name).first():
                continue
            d = Document(filename=p.name, file_type="md", source_path=str(p), meta={})
            s.add(d); s.commit(); did = d.id
        print(p.name, (await index_document(did)).status)

asyncio.run(main())
