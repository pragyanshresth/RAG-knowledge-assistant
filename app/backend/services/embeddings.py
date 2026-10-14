from openai import AsyncOpenAI
from backend.core.config import settings

_client: AsyncOpenAI | None = None


def openai_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        _client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url or None)
    return _client


async def embed(texts: list[str]) -> list[list[float]]:
    out: list[list[float]] = []
    for i in range(0, len(texts), 64):
        r = await openai_client().embeddings.create(model=settings.embedding_model, input=texts[i:i + 64])
        out += [d.embedding for d in r.data]
    return out
