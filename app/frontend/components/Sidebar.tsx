"use client";
import { useRef, useState } from "react";
import { Doc, reindex, uploadAndIndex } from "@/lib/api";

export default function Sidebar({ docs, refresh }: { docs: Doc[]; refresh: () => void }) {
  const input = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const run = async (fn: () => Promise<unknown>) => {
    setBusy(true); setErr("");
    try { await fn(); } catch (e) { setErr((e as Error).message); } finally { setBusy(false); refresh(); }
  };
  return (
    <aside className="w-72 shrink-0 border-r border-white/10 p-4 flex flex-col gap-3">
      <h2 className="font-semibold">Documents</h2>
      <input ref={input} type="file" hidden accept=".pdf,.txt,.md,.docx"
        onChange={(e) => e.target.files?.[0] && run(() => uploadAndIndex(e.target.files![0]))} />
      <button disabled={busy} onClick={() => input.current?.click()}
        className="rounded-lg bg-indigo-600 py-2 text-sm hover:bg-indigo-500 disabled:opacity-50">
        {busy ? "Working…" : "Upload document"}
      </button>
      {err && <p className="text-xs text-red-400">{err}</p>}
      <ul className="space-y-2 overflow-y-auto text-sm">
        {docs.map((d) => (
          <li key={d.id} className="rounded-lg bg-white/5 p-2">
            <div className="truncate">{d.filename}</div>
            <div className="flex justify-between text-xs text-gray-400">
              <span className={d.status === "failed" ? "text-red-400" : d.status === "indexed" ? "text-emerald-400" : ""}>
                {d.status}{d.metadata.chunks ? ` · ${d.metadata.chunks} chunks` : ""}
              </span>
              <button className="underline" disabled={busy} onClick={() => run(() => reindex(d.id))}>reindex</button>
            </div>
            {d.metadata.error && <div className="text-xs text-red-400">{d.metadata.error}</div>}
          </li>
        ))}
        {!docs.length && <li className="text-gray-500">No documents yet.</li>}
      </ul>
    </aside>
  );
}
