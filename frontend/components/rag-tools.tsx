"use client";

import { useAuth } from "@clerk/nextjs";
import { useState } from "react";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function RagTools() {
  const { getToken } = useAuth();
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [status, setStatus] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const uploadDocument = async () => {
    if (!file) return;
    setStatus("Uploading and indexing...");
    const token = await getToken();
    const formData = new FormData();
    formData.append("file", file);
    formData.append("faculty", "Engineering");
    formData.append("course", "Computer Science");
    formData.append("module", "Data Structures");
    formData.append("topic", "General");
    formData.append("year", "2026");
    formData.append("document_type", "Lecture Note");
    const res = await fetch(`${apiBase}/api/v1/documents/upload`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token ?? ""}`
      },
      body: formData
    });
    if (!res.ok) {
      setStatus("Upload failed");
      return;
    }
    setStatus("Upload complete");
  };

  const askQuestion = async () => {
    setStatus("Querying RAG...");
    const token = await getToken();
    try {
      const res = await fetch(`${apiBase}/api/v1/rag/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token ?? ""}`
        },
        body: JSON.stringify({ question, metadata_filter: {} })
      });
      const json = await res.json();
      if (!res.ok) {
        setAnswer(json.detail ?? "RAG request failed");
        setStatus("Request failed");
        return;
      }
      setAnswer(json.answer ?? "No answer");
      setStatus("Done");
    } catch (error) {
      setAnswer(`Network error: ${error instanceof Error ? error.message : "unknown error"}`);
      setStatus("Request failed");
    }
  };

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
      <h2 className="text-lg font-semibold">Knowledge Base</h2>
      <p className="mt-1 text-sm text-slate-400">Upload notes and query answers grounded in your materials.</p>
      <input
        className="mt-4 block w-full rounded-md border border-slate-700 bg-slate-950 p-2"
        type="file"
        accept=".pdf,.txt"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />
      <button className="mt-3 rounded-md bg-emerald-600 px-4 py-2" onClick={uploadDocument} type="button">
        Upload
      </button>

      <h2 className="mt-6 text-lg font-semibold">Ask From Materials</h2>
      <textarea
        className="mt-3 w-full rounded-md border border-slate-700 bg-slate-950 p-3"
        rows={4}
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question from uploaded notes..."
      />
      <button className="mt-3 rounded-md bg-blue-600 px-4 py-2" onClick={askQuestion} type="button">
        Ask
      </button>
      <p className="mt-3 text-sm text-slate-400">{status}</p>
      {answer ? <p className="mt-2 whitespace-pre-wrap text-slate-200">{answer}</p> : null}
    </section>
  );
}
