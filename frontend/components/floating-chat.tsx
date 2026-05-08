"use client";

import { useAuth } from "@clerk/nextjs";
import { FormEvent, useRef, useState } from "react";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export function FloatingChat() {
  const { getToken } = useAuth();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [studentName, setStudentName] = useState("");
  const [awaitingName, setAwaitingName] = useState(true);
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content: "Hi! I am your academic assistant. What is your name so I can address you properly?"
    }
  ]);

  const sendMessage = async (e: FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");

    if (awaitingName) {
      setStudentName(text);
      setAwaitingName(false);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Nice to meet you, ${text}. You can ask about your modules, tests, exams, assignments, or study plan.`
        }
      ]);
      return;
    }

    setLoading(true);
    try {
      const token = await getToken();
      const res = await fetch(`${apiBase}/api/v1/agents/route`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token ?? ""}`
        },
        body: JSON.stringify({ query: text, context: { channel: "floating-chat", student_name: studentName } })
      });
      const json = await res.json();
      const reply = json.response ?? json.detail ?? "I could not process that message.";
      setMessages((prev) => [...prev, { role: "assistant", content: String(reply) }]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Network error: ${error instanceof Error ? error.message : "unknown error"}`
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const uploadFileFromChat = async (file: File) => {
    setLoading(true);
    try {
      const token = await getToken();
      const formData = new FormData();
      formData.append("file", file);
      formData.append("faculty", "Engineering");
      formData.append("course", "Computer Science");
      formData.append("module", "General");
      formData.append("topic", "General");
      formData.append("year", "2026");
      formData.append("document_type", "Chat Upload");
      const res = await fetch(`${apiBase}/api/v1/documents/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token ?? ""}`
        },
        body: formData
      });
      const json = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.ok
            ? `Uploaded ${json.source ?? file.name} and indexed ${json.chunks ?? 0} chunks.`
            : `Upload failed: ${json.detail ?? "unknown error"}`
        }
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Upload error: ${error instanceof Error ? error.message : "unknown error"}` }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        type="button"
        aria-label="Open chat assistant"
        onClick={() => setOpen((v) => !v)}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-2xl shadow-lg shadow-blue-900/40 transition hover:bg-blue-500"
      >
        💬
      </button>

      {open ? (
        <section className="fixed bottom-24 right-6 z-50 flex h-[70vh] w-[min(380px,92vw)] flex-col overflow-hidden rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl">
          <div className="flex items-center justify-between border-b border-slate-700 px-4 py-3">
            <h3 className="font-semibold">Academic Assistant</h3>
            <button
              type="button"
              className="rounded px-2 py-1 text-slate-300 hover:bg-slate-800"
              onClick={() => setOpen(false)}
            >
              Close
            </button>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto p-4">
            {messages.map((message, idx) => (
              <div
                key={`${message.role}-${idx}`}
                className={`max-w-[90%] rounded-xl px-3 py-2 text-sm ${
                  message.role === "user"
                    ? "ml-auto bg-blue-600 text-white"
                    : "bg-slate-800 text-slate-100"
                }`}
              >
                {message.content}
              </div>
            ))}
            {loading ? (
              <div className="max-w-[90%] rounded-xl bg-slate-800 px-3 py-2 text-sm text-slate-100">
                Assistant is typing...
              </div>
            ) : null}
          </div>

          <form onSubmit={sendMessage} className="border-t border-slate-700 p-3">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm"
                title="Upload file"
              >
                +
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) void uploadFileFromChat(file);
                  e.currentTarget.value = "";
                }}
              />
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your question..."
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none ring-blue-500 focus:ring-2"
              />
              <button
                type="submit"
                disabled={loading}
                className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium disabled:opacity-60"
              >
                {loading ? "..." : "Send"}
              </button>
            </div>
          </form>
        </section>
      ) : null}
    </>
  );
}
