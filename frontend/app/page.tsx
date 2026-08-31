"use client";

import {
  useEffect,
  useRef,
  useState,
  type ChangeEvent,
  type FormEvent,
  type KeyboardEvent,
} from "react";

import { queryAgent, uploadDocument } from "@/lib/api";

type Message = {
  role: "user" | "assistant" | "system";
  content: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [documentId, setDocumentId] = useState<string>();
  const [documentName, setDocumentName] = useState<string>();

  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, uploading]);

  async function sendMessage(query: string) {
    setMessages((prev) => [...prev, { role: "user", content: query }]);
    setLoading(true);
    setError("");

    try {
      const data = await queryAgent(query, documentId);
      setMessages((prev) => [...prev, { role: "assistant", content: data.answer }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
    sendMessage(trimmed);
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as FormEvent);
    }
  }

  function handleInputChange(e: ChangeEvent<HTMLTextAreaElement>) {
    setInput(e.target.value);
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
    }
  }

  async function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;

    setUploading(true);
    setError("");

    try {
      const data = await uploadDocument(file);
      setDocumentId(data.document_id);
      setDocumentName(data.filename);
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content: `Uploaded "${data.filename}" (${data.chunk_count} chunks indexed). Ask away!`,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  function clearDocument() {
    setDocumentId(undefined);
    setDocumentName(undefined);
  }

  return (
    <div className="flex h-screen flex-col bg-zinc-50 font-sans dark:bg-black">
      <header className="border-b border-black/10 px-4 py-3 dark:border-white/10">
        <h1 className="text-lg font-semibold text-black dark:text-zinc-50">RAG Agent</h1>
      </header>

      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto flex max-w-3xl flex-col gap-4 px-4 py-6">
          {messages.length === 0 && !loading && !uploading && (
            <p className="mt-20 text-center text-zinc-400">
              Ask a question, or upload a document to chat about it.
            </p>
          )}

          {messages.map((m, i) =>
            m.role === "system" ? (
              <p key={i} className="text-center text-xs text-zinc-500 dark:text-zinc-400">
                {m.content}
              </p>
            ) : (
              <div
                key={i}
                className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                    m.role === "user"
                      ? "bg-black text-white dark:bg-zinc-50 dark:text-black"
                      : "bg-white text-black dark:bg-zinc-900 dark:text-zinc-50"
                  }`}
                >
                  {m.content}
                </div>
              </div>
            )
          )}

          {(loading || uploading) && (
            <div className="flex justify-start">
              <div className="flex items-center gap-1 rounded-2xl bg-white px-4 py-3 dark:bg-zinc-900">
                <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.3s]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.15s]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400" />
              </div>
            </div>
          )}

          {error && <p className="text-center text-sm text-red-500">{error}</p>}

          <div ref={bottomRef} />
        </div>
      </div>

      <form
        onSubmit={handleSubmit}
        className="border-t border-black/10 px-4 py-4 dark:border-white/10"
      >
        <div className="mx-auto flex max-w-3xl flex-col gap-2">
          {documentName && (
            <div className="flex w-fit items-center gap-2 rounded-full bg-white px-3 py-1 text-xs text-black dark:bg-zinc-900 dark:text-zinc-50">
              <span>📄 {documentName}</span>
              <button
                type="button"
                onClick={clearDocument}
                className="text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300"
                aria-label="Remove document"
              >
                ×
              </button>
            </div>
          )}

          <div className="flex items-end gap-2">
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.md,.pdf,.docx"
              onChange={handleFileChange}
              className="hidden"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              title="Attach a document"
              className="rounded-full border border-black/10 px-3 py-3 text-sm text-black transition-colors hover:bg-black/5 disabled:opacity-40 dark:border-white/10 dark:text-zinc-50 dark:hover:bg-white/10"
            >
              📎
            </button>
            <textarea
              ref={textareaRef}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Message RAG Agent..."
              rows={1}
              className="max-h-40 flex-1 resize-none rounded-2xl border border-black/10 bg-white p-3 text-sm text-black outline-none dark:border-white/10 dark:bg-zinc-900 dark:text-zinc-50"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="rounded-full bg-foreground px-5 py-3 text-sm font-medium text-background transition-colors hover:bg-[#383838] disabled:opacity-40 dark:hover:bg-[#ccc]"
            >
              Send
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
