"use client";

import { FormEvent, useRef, useState } from "react";

type Tone = "professional" | "casual" | "bold" | "friendly" | "educational";
type Language = "English" | "Indonesian";

type FormState = {
  topic: string;
  tone: Tone;
  audience: string;
  language: Language;
  count: number;
  include_hashtags: boolean;
  max_chars: number;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const initialForm: FormState = {
  topic: "Build a realtime AI content generator with FastAPI, Next.js, SSE, and Kimi API",
  tone: "professional",
  audience: "software developers and startup founders",
  language: "English",
  count: 3,
  include_hashtags: true,
  max_chars: 280,
};

export default function Home() {
  const [form, setForm] = useState<FormState>(initialForm);
  const [content, setContent] = useState("");
  const [status, setStatus] = useState("Idle");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState("");
  const eventSourceRef = useRef<EventSource | null>(null);

  function updateForm<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function stopStream() {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
    setIsStreaming(false);
    setStatus("Stopped");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (isStreaming) return;

    setContent("");
    setError("");
    setStatus("Creating SSE session...");
    setIsStreaming(true);

    try {
      const sessionResponse = await fetch(`${API_URL}/api/twitter/sessions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      if (!sessionResponse.ok) {
        const text = await sessionResponse.text();
        throw new Error(text || "Failed to create generation session");
      }

      const session = await sessionResponse.json();
      const sseUrl = `${API_URL}${session.sse_url}`;

      setStatus("Connecting to SSE...");

      const eventSource = new EventSource(sseUrl);
      eventSourceRef.current = eventSource;

      eventSource.addEventListener("start", (event) => {
        const data = JSON.parse(event.data);
        setStatus(`Streaming from ${data.model}`);
      });

      eventSource.addEventListener("token", (event) => {
        const data = JSON.parse(event.data);
        setContent((prev) => prev + data.token);
      });

      eventSource.addEventListener("final", () => {
        setStatus("Finalizing...");
      });

      eventSource.addEventListener("done", () => {
        setStatus("Done");
        setIsStreaming(false);
        eventSource.close();
        eventSourceRef.current = null;
      });

      eventSource.addEventListener("error", (event) => {
        let message = "SSE connection error";

        if ("data" in event && typeof event.data === "string") {
          try {
            message = JSON.parse(event.data).message || message;
          } catch {
            message = event.data || message;
          }
        }

        setError(message);
        setStatus("Error");
        setIsStreaming(false);
        eventSource.close();
        eventSourceRef.current = null;
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
      setStatus("Error");
      setIsStreaming(false);
    }
  }

  return (
    <main className="page">
      <section className="hero">
        <div className="badge">FastAPI + Next.js + SSE + Kimi + DSPy/GEPA</div>
        <h1>Realtime Twitter Content Generator</h1>
        <p>
          This demo sends a POST request to FastAPI, opens an SSE connection with
          EventSource, and streams Kimi tokens back into the UI in realtime. DSPy
          + GEPA files are included for offline prompt optimization.
        </p>
      </section>

      <section className="grid">
        <form className="card form" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="topic">Topic / brief</label>
            <textarea
              id="topic"
              value={form.topic}
              onChange={(event) => updateForm("topic", event.target.value)}
              placeholder="What should the tweets be about?"
              required
            />
          </div>

          <div className="row">
            <div className="field">
              <label htmlFor="tone">Tone</label>
              <select
                id="tone"
                value={form.tone}
                onChange={(event) => updateForm("tone", event.target.value as Tone)}
              >
                <option value="professional">Professional</option>
                <option value="casual">Casual</option>
                <option value="bold">Bold</option>
                <option value="friendly">Friendly</option>
                <option value="educational">Educational</option>
              </select>
            </div>

            <div className="field">
              <label htmlFor="language">Language</label>
              <select
                id="language"
                value={form.language}
                onChange={(event) => updateForm("language", event.target.value as Language)}
              >
                <option value="English">English</option>
                <option value="Indonesian">Indonesian</option>
              </select>
            </div>
          </div>

          <div className="field">
            <label htmlFor="audience">Audience</label>
            <input
              id="audience"
              value={form.audience}
              onChange={(event) => updateForm("audience", event.target.value)}
              placeholder="software developers, founders, marketers..."
            />
          </div>

          <div className="row">
            <div className="field">
              <label htmlFor="count">Tweet count</label>
              <input
                id="count"
                type="number"
                min={1}
                max={5}
                value={form.count}
                onChange={(event) => updateForm("count", Number(event.target.value))}
              />
            </div>

            <div className="field">
              <label htmlFor="max-chars">Max chars</label>
              <input
                id="max-chars"
                type="number"
                min={120}
                max={280}
                value={form.max_chars}
                onChange={(event) => updateForm("max_chars", Number(event.target.value))}
              />
            </div>
          </div>

          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={form.include_hashtags}
              onChange={(event) => updateForm("include_hashtags", event.target.checked)}
            />
            Allow up to 2 useful hashtags
          </label>

          <div className="actions">
            <button className="primary-btn" type="submit" disabled={isStreaming}>
              {isStreaming ? "Generating..." : "Generate with SSE"}
            </button>
            <button className="secondary-btn" type="button" onClick={stopStream} disabled={!isStreaming}>
              Stop
            </button>
          </div>

          {error ? <div className="note error-text">{error}</div> : null}
          <div className="note">
            API URL: {API_URL}. Paste your Kimi token in <code>backend/.env</code>,
            then run <code>./start.sh</code>.
          </div>
        </form>

        <div className="card">
          <div className="output-header">
            <h2>Streaming output</h2>
            <div className="status">
              <span className={`dot ${isStreaming ? "live" : status === "Error" ? "error" : ""}`} />
              {status}
            </div>
          </div>

          <div className={`output ${content ? "" : "placeholder"}`}>
            {content || "Your generated Twitter/X content will stream here token by token..."}
          </div>

          <div className="note">
            Method: <strong>POST /api/twitter/sessions</strong> then
            <strong> GET /api/twitter/sse/{"{session_id}"}</strong> using browser EventSource.
          </div>
        </div>
      </section>
    </main>
  );
}
