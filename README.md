# RAG Internal Knowledge Assistant

Upload internal documents (PDF, TXT, MD, DOCX), index them, and ask questions in plain English. Answers are **grounded** in retrieved chunks, cite their sources, and fall back to "not found" when nothing relevant exists.

**Stack:** Next.js + TypeScript + Tailwind · FastAPI · any OpenAI-compatible provider (free Gemini by default; Ollama or OpenAI also work) · Qdrant (embedded local mode or server) · SQLite.

## Architecture
upload → parse (PyMuPDF / python-docx / markdown headings) → overlapping chunks → OpenAI embeddings → Qdrant, with chunk metadata in SQLite.
query → embed question → top-k search with score threshold (`MIN_SCORE`) → no hits: fallback answer without calling the LLM → otherwise the LLM answers from context only and returns JSON (answer, used sources, confidence, follow-ups).

## Setup (local)
```bash
cp .env.example .env            # add a free Gemini key from https://aistudio.google.com/apikey
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=app
python -m backend.seed          # indexes data/sample_docs
uvicorn backend.main:app --reload   # http://localhost:8000/docs
# new terminal
cd app/frontend && npm install && npm run dev   # http://localhost:3000
```
## Docker
`cp .env.example .env` (add key), then `docker compose up --build`. UI :3000, API :8000, Qdrant as a service.

## Environment variables
See `.env.example` for the Gemini (free), Ollama (free, local) and OpenAI presets. If you switch provider/model, delete `data/qdrant` and `data/app.db` and re-seed, because vector sizes differ. Also: `CHUNK_SIZE`, `CHUNK_OVERLAP`, `MAX_UPLOAD_MB`, `DATABASE_URL`, `CORS_ORIGINS`, `QDRANT_PATH`.

## API
| Endpoint | Purpose |
|---|---|
| `GET /health` | liveness |
| `POST /documents/upload` | multipart `file`; returns Document (status `uploaded`); 415 for unsupported types |
| `POST /documents/index` | `{"document_ids": [...]}` or `{}` for all; calling again re-indexes |
| `GET /documents` | list with status and metadata |
| `POST /query` | `{"question": "..."}` → `{answer, sources[], retrieved_chunks[], confidence, follow_up_questions[]}` |

## Demo
Ask the questions in `data/sample_docs/sample_queries.md` (the last one shows the not-found fallback).

## Tests
`PYTHONPATH=app pytest tests` — chunking, upload validation, indexing and low-relevance fallback (OpenAI stubbed; no key needed).

## Limitations / next steps
No auth, no reranker (score-threshold filtering only), no streaming, documents list lives in the chat sidebar rather than its own page.
