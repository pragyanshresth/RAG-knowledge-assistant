import asyncio
from qdrant_client import QdrantClient, models
from backend.core.config import settings

COLLECTION = "chunks"
_client: QdrantClient | None = None


def client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.qdrant_url) if settings.qdrant_url else QdrantClient(path=settings.qdrant_path)
    return _client


def _ensure_collection(dim: int):
    c = client()
    if not c.collection_exists(COLLECTION):
        c.create_collection(COLLECTION, vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE))
        return
    existing = c.get_collection(COLLECTION).config.params.vectors.size
    if existing != dim:
        raise RuntimeError(f"Embedding size changed ({existing} -> {dim}) after switching models/provider. "
                           "Delete data/qdrant and data/app.db, then re-index.")


def _upsert(ids, vectors, payloads):
    _ensure_collection(len(vectors[0]))
    client().upsert(COLLECTION, points=[models.PointStruct(id=i, vector=v, payload=p)
                                        for i, v, p in zip(ids, vectors, payloads)])


def _delete_doc(doc_id):
    if not client().collection_exists(COLLECTION):
        return
    client().delete(COLLECTION, points_selector=models.FilterSelector(filter=models.Filter(
        must=[models.FieldCondition(key="document_id", match=models.MatchValue(value=doc_id))])))


def _search(vector, k, min_score):
    if not client().collection_exists(COLLECTION):
        return []  # nothing indexed yet
    return client().query_points(COLLECTION, query=vector, limit=k, score_threshold=min_score,
                                 with_payload=True).points


async def upsert(ids, vectors, payloads): await asyncio.to_thread(_upsert, ids, vectors, payloads)
async def delete_document(doc_id): await asyncio.to_thread(_delete_doc, doc_id)
async def search(vector, k, min_score): return await asyncio.to_thread(_search, vector, k, min_score)
