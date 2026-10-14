"use client";
import { useCallback, useEffect, useState } from "react";
import Chat from "@/components/Chat";
import Sidebar from "@/components/Sidebar";
import { Doc, listDocs } from "@/lib/api";

export default function Home() {
  const [docs, setDocs] = useState<Doc[]>([]);
  const refresh = useCallback(() => { listDocs().then(setDocs).catch(() => {}); }, []);
  useEffect(refresh, [refresh]);
  return <main className="flex h-screen"><Sidebar docs={docs} refresh={refresh} /><Chat /></main>;
}
