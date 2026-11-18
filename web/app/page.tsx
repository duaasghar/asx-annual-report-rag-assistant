"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { isAskResponse, MAX_QUESTION_LENGTH, type AskResponse, type Source } from "@/lib/types";

type Message =
  | { role: "user"; text: string }
  | { role: "assistant"; data: AskResponse }
  | { role: "error"; text: string };

const EXAMPLES = [
  "What was ASX's operating revenue in FY2025?",
  "What dividend per share did ASX pay?",
  "What was statutory net profit after tax?",
];

function citedPages(sources: Source[]): number[] {
  const pages = sources.map((s) => s.page).filter((p): p is number => p !== null);
  return [...new Set(pages)].sort((a, b) => a - b);
}

async function fetchAnswer(question: string): Promise<Message> {
  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data: unknown = await res.json().catch(() => null);
    if (res.ok && isAskResponse(data)) return { role: "assistant", data };
    const message =
      typeof data === "object" && data !== null && "error" in data && typeof data.error === "string"
        ? data.error
        : "Something went wrong. Please try again.";
    return { role: "error", text: message };
  } catch {
    return { role: "error", text: "Network error. Please check your connection and try again." };
  }
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function ask(q: string) {
    const trimmed = q.trim();
    if (!trimmed || loading) return;
    setMessages((m) => [...m, { role: "user", text: trimmed }]);
    setQuestion("");
    setLoading(true);
    const reply = await fetchAnswer(trimmed);
    setMessages((m) => [...m, reply]);
    setLoading(false);
  }

  return (
    <main className="mx-auto w-full max-w-2xl px-4 py-8 sm:px-6">
      <h1 className="text-2xl font-semibold">ASX FY2025 Annual Report Assistant</h1>
      <p className="mt-1 text-sm opacity-70">
        Answers come only from the ASX FY2025 annual report, with page citations. If the report
        doesn&apos;t say, the assistant tells you.
      </p>

      <div className="mt-4 flex flex-wrap gap-2">
        {EXAMPLES.map((e) => (
          <button
            key={e}
            type="button"
            onClick={() => ask(e)}
            disabled={loading}
            className="rounded-full border border-current/20 px-3 py-1 text-sm hover:bg-current/5 disabled:opacity-50"
          >
            {e}
          </button>
        ))}
      </div>

      <div className="mt-6 space-y-4" aria-live="polite">
        {messages.map((m, i) => {
          if (m.role === "user") {
            return (
              <p key={i} className="font-medium">
                You: {m.text}
              </p>
            );
          }
          if (m.role === "error") {
            return (
              <p key={i} role="alert" className="rounded border border-red-500/40 p-3 text-red-600 dark:text-red-400">
                {m.text}
              </p>
            );
          }
          const pages = citedPages(m.data.sources);
          return (
            <div key={i} className="rounded-lg border border-current/15 p-4">
              <div className="space-y-2 [&_li]:ml-5 [&_ul]:list-disc [&_ol]:list-decimal [&_strong]:font-semibold">
                <ReactMarkdown>{m.data.answer}</ReactMarkdown>
              </div>
              {m.data.sources.length > 0 && (
                <details className="mt-3 text-sm opacity-80">
                  <summary className="cursor-pointer">
                    Sources{pages.length > 0 && `: page${pages.length > 1 ? "s" : ""} ${pages.join(", ")}`}
                  </summary>
                  <ul className="mt-2 space-y-2">
                    {m.data.sources.map((s, j) => (
                      <li key={j} className="border-l-2 border-current/20 pl-3">
                        <span className="font-medium">{s.page !== null ? `p.${s.page}` : "Unknown page"}:</span>{" "}
                        {s.excerpt}…
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          );
        })}
        {loading && (
          <p className="animate-pulse opacity-60">
            Thinking… (the first question can take ~30s while the server wakes up)
          </p>
        )}
        <div ref={bottomRef} />
      </div>

      <form
        className="mt-6 flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          void ask(question);
        }}
      >
        <label htmlFor="question" className="sr-only">
          Your question
        </label>
        <input
          id="question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          maxLength={MAX_QUESTION_LENGTH}
          placeholder="Ask about the ASX FY2025 annual report…"
          className="min-w-0 flex-1 rounded border border-current/20 bg-transparent px-3 py-2"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="rounded bg-foreground px-4 py-2 text-background disabled:opacity-50"
        >
          Ask
        </button>
      </form>
    </main>
  );
}
