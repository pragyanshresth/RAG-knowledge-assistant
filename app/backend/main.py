from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
from backend.core.config import settings
from backend.models.db import init_db
from fastapi.responses import RedirectResponse

init_db()
app = FastAPI(title="RAG Internal Knowledge Assistant", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(","),
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(router)
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs")