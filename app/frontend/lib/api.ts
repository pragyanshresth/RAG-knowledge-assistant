const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
export type Doc = { id: string; filename: string; status: string; file_type: string; metadata: { chunks?: number; error?: string } };
export type Source = { document: string; section: string; score: number };
export type Chunk = Source & { text: string; chunk_index: number };
export type Result = { answer: string; sources: Source[]; retrieved_chunks: Chunk[]; confidence: string; follow_up_questions: string[] };

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(BASE + path, init);
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail ?? `Request failed (${r.status})`);
  return r.json();
}
const post = (body: unknown): RequestInit => ({ method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
export const listDocs = () => call<Doc[]>("/documents");
export const ask = (question: string) => call<Result>("/query", post({ question }));
export const reindex = (id: string) => call<Doc[]>("/documents/index", post({ document_ids: [id] }));
export async function uploadAndIndex(file: File) {
  const fd = new FormData(); fd.append("file", file);
  const d = await call<Doc>("/documents/upload", { method: "POST", body: fd });
  return reindex(d.id);
}
