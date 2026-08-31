"use client";

import { useState, type FormEvent } from "react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    setAnswer("");

    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) throw new Error(`Request failed: ${res.status}`);

      const data = await res.json();
      setAnswer(data.answer);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-1 flex-col items-center justify-center bg-zinc-50 px-4 font-sans dark:bg-black">
      <main className="flex w-full max-w-xl flex-col gap-6 py-16">
        <h1 className="text-2xl font-semibold text-black dark:text-zinc-50">
          RAG Agent
        </h1>

        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question..."
            rows={3}
            className="rounded-lg border border-black/10 bg-white p-3 text-black dark:border-white/10 dark:bg-zinc-900 dark:text-zinc-50"
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded-full bg-foreground px-5 py-3 text-background transition-colors hover:bg-[#383838] disabled:opacity-50 dark:hover:bg-[#ccc]"
          >
            {loading ? "Thinking..." : "Ask"}
          </button>
        </form>

        {error && <p className="text-red-500">{error}</p>}

        {answer && (
          <div className="rounded-lg border border-black/10 bg-white p-4 text-black dark:border-white/10 dark:bg-zinc-900 dark:text-zinc-50">
            {answer}
          </div>
        )}
      </main>
    </div>
  );
}
