"use client";
import { useState } from "react";
import { ask, Result } from "@/lib/api";

type Turn = { q: string; r?: Result; error?: string };
const badge: Record<string, string> = { high: "bg-emerald-600", medium: "bg-amber-600", low: "bg-orange-700", none: "bg-gray-600" };

export default function Chat() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState<Result | null>(null);

  const submit = async (question: string) => {
    if (!question.trim() || loading) return;
    setQ(""); setLoading(true);
    setTurns((t) => [...t, { q: question }]);
    try {
      const r = await ask(question); setOpen(r);
      setTurns((t) => [...t.slice(0, -1), { q: question, r }]);
    } catch (e) {
      setTurns((t) => [...t.slice(0, -1), { q: question, error: (e as Error).message }]);
    } finally { setLoading(false); }
  };

  return (
    <div className="flex flex-1 min-w-0">
      <section className="flex flex-1 flex-col min-w-0">
        <header className="border-b border-white/10 p-4 flex items-center gap-2">
          <h1 className="font-semibold">Internal Knowledge Assistant</h1>
          <span className="rounded-full bg-indigo-500/20 px-2 py-0.5 text-xs text-indigo-300">Grounded answers</span>
        </header>
        <div className="flex-1 space-y-6 overflow-y-auto p-6">
          {!turns.length && <p className="text-gray-500">Ask something about your uploaded documents, e.g. “What is the remote work eligibility policy?”</p>}
          {turns.map((t, i) => (
            <div key={i} className="space-y-2">
              <div className="ml-auto w-fit max-w-xl rounded-2xl bg-indigo-600 px-4 py-2">{t.q}</div>
              {t.error && <div className="rounded-2xl bg-red-950 px-4 py-2 text-red-300">{t.error}</div>}
              {t.r && (
                <div className="max-w-2xl rounded-2xl bg-white/5 p-4 space-y-3">
                  <p className="whitespace-pre-wrap">{t.r.answer}</p>
                  <div className="flex flex-wrap items-center gap-2 text-xs">
                    <span className={`rounded px-2 py-0.5 ${badge[t.r.confidence]}`}>confidence: {t.r.confidence}</span>
                    {t.r.sources.map((s, j) => (
                      <button key={j} onClick={() => setOpen(t.r!)} className="rounded border border-white/20 px-2 py-0.5 hover:bg-white/10">
                        {s.document} · {s.section} · {s.score}
                      </button>
                    ))}
                  </div>
                  {t.r.follow_up_questions.map((f) => (
                    <button key={f} onClick={() => submit(f)} className="block text-left text-xs text-indigo-300 hover:underline">↳ {f}</button>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && <div className="animate-pulse text-gray-400">Searching documents…</div>}
        </div>
        <form onSubmit={(e) => { e.preventDefault(); submit(q); }} className="flex gap-2 border-t border-white/10 p-4">
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Ask a question…"
            className="flex-1 rounded-lg bg-white/5 px-4 py-2 outline-none focus:ring-1 ring-indigo-500" />
          <button disabled={loading} className="rounded-lg bg-indigo-600 px-4 hover:bg-indigo-500 disabled:opacity-50">Ask</button>
        </form>
      </section>
      <aside className="hidden w-96 shrink-0 overflow-y-auto border-l border-white/10 p-4 lg:block">
        <h2 className="mb-3 font-semibold">Sources & snippets</h2>
        {open ? open.retrieved_chunks.map((c, i) => (
          <div key={i} className="mb-3 rounded-lg bg-white/5 p-3 text-xs">
            <div className="mb-1 text-gray-400">{c.document} · {c.section} · score {c.score}</div>
            <p className="text-gray-200">{c.text}</p>
          </div>
        )) : <p className="text-sm text-gray-500">Retrieved excerpts appear here.</p>}
        {open && !open.retrieved_chunks.length && <p className="text-sm text-gray-500">No relevant excerpts found.</p>}
      </aside>
    </div>
  );
}
