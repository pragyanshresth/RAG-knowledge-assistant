import json
import re
from backend.core.config import settings
from backend.schemas.schemas import QueryResult, RetrievedChunk, Source
from backend.services import vectorstore
from backend.services.embeddings import embed, openai_client

SYSTEM_PROMPT = (
    "You are an internal knowledge assistant. Answer questions using only the provided context. "
    "If the answer is not present in the context, say that it could not be found in the provided documents. "
    "Always cite the source documents used. Keep answers concise and professional.\n"
    'Respond with JSON only: {"answer": str (cite as [n]), "used": [int context numbers], '
    '"confidence": "high"|"medium"|"low", "follow_up_questions": [up to 3 strings]}'
)
NOT_FOUND = "I couldn't find this in the provided documents."


def _parse_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?|```$", "", (text or "").strip(), flags=re.M).strip()
    try:
        return json.loads(text)
    except ValueError:
        m = re.search(r"\{.*\}", text, re.S)
        return json.loads(m.group(0)) if m else {"answer": text, "used": [], "confidence": "low"}


async def answer_question(question: str, top_k: int | None = None) -> QueryResult:
    qvec = (await embed([question]))[0]
    hits = await vectorstore.search(qvec, top_k or settings.top_k, settings.min_score)
    if not hits:  # graceful fallback: never call the LLM without grounding
        return QueryResult(answer=NOT_FOUND, sources=[], retrieved_chunks=[], confidence="none")
    context = "\n\n".join(f"[{n}] {h.payload['document']} — {h.payload['section']}\n{h.payload['text']}"
                          for n, h in enumerate(hits, 1))
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}]
    try:
        r = await openai_client().chat.completions.create(
            model=settings.chat_model, temperature=0, response_format={"type": "json_object"}, messages=messages)
    except Exception:  # some providers/models don't support JSON mode
        r = await openai_client().chat.completions.create(model=settings.chat_model, temperature=0, messages=messages)
    data = _parse_json(r.choices[0].message.content)
    used = {n for n in data.get("used", []) if isinstance(n, int) and 1 <= n <= len(hits)}
    cited = [h for n, h in enumerate(hits, 1) if n in used]
    chunks = [RetrievedChunk(document=h.payload["document"], section=h.payload["section"],
                             chunk_index=h.payload["chunk_index"], text=h.payload["text"],
                             score=round(h.score, 3)) for h in hits]
    seen, sources = set(), []
    for h in cited:
        key = (h.payload["document"], h.payload["section"])
        if key not in seen:
            seen.add(key)
            sources.append(Source(document=key[0], section=key[1], score=round(h.score, 3)))
    conf = data.get("confidence", "low") if sources else "none"
    return QueryResult(answer=data.get("answer", NOT_FOUND), sources=sources, retrieved_chunks=chunks,
                       confidence=conf, follow_up_questions=data.get("follow_up_questions", [])[:3])
