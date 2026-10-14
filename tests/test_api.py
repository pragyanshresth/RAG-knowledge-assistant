import hashlib
from fastapi.testclient import TestClient
from backend.main import app
from backend.services import ingest, rag

client = TestClient(app)


async def fake_embed(texts):  # deterministic bag-of-words vectors, 1536-d
    out = []
    for t in texts:
        v = [0.0] * 1536
        for w in t.lower().split():
            v[int(hashlib.md5(w.encode()).hexdigest(), 16) % 1536] += 1
        out.append(v)
    return out


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_rejects_unsupported():
    assert client.post("/documents/upload", files={"file": ("a.exe", b"x")}).status_code == 415


def test_upload_index_and_retrieval_fallback(monkeypatch):
    monkeypatch.setattr(ingest, "embed", fake_embed)
    monkeypatch.setattr(rag, "embed", fake_embed)
    d = client.post("/documents/upload", files={"file": ("p.md", b"# Remote\n## 3.4\nRemote work after six months.")}).json()
    assert client.post("/documents/index", json={"document_ids": [d["id"]]}).json()[0]["status"] == "indexed"
    assert client.get("/documents").json()[0]["filename"] == "p.md"
    r = client.post("/query", json={"question": "zebra quantum banana"}).json()
    assert r["confidence"] == "none" and r["sources"] == []
