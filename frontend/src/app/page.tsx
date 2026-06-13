"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

type Tone = "professional" | "casual" | "bold" | "friendly" | "educational";
type Language = "English" | "Indonesian";
type Provider = "gemini" | "groq" | "ollama";

type AspectScores = {
  hook: number;
  clarity: number;
  relevance: number;
  naturalness: number;
  constraint_fit: number;
};

type ArtifactPreview = {
  topic: string;
  score: number;
  aspect_scores: AspectScores;
  notes: string[];
  tweet_count: number;
  tweets: string;
};

type ComparisonPreview = {
  topic: string;
  baseline_score: number;
  optimized_score: number;
  score_delta: number;
  aspect_delta: Record<string, number>;
  improved_aspects?: string[];
  weaker_aspects?: string[];
  baseline_tweets: string;
  optimized_tweets: string;
  baseline_notes: string[];
  optimized_notes: string[];
};

type PromptVersions = {
  baseline_runtime_prompt?: string;
  optimized_runtime_prompt?: string;
  baseline_dspy_instructions?: string | null;
  optimized_dspy_instructions?: string | null;
};

type OptimizerArtifact = {
  generated_at: string;
  model: string;
  baseline_validation_score: number;
  optimized_validation_score: number;
  score_delta: number;
  score_weights: Record<string, number>;
  scoring_guide: Record<string, string>;
  how_to_judge?: string[];
  prompt_change_summary?: string[];
  prompt_versions?: PromptVersions;
  baseline_preview: ArtifactPreview[];
  optimized_preview: ArtifactPreview[];
  comparison_preview: ComparisonPreview[];
};

type FormState = {
  topic: string;
  provider: Provider;
  tone: Tone;
  audience: string;
  language: Language;
  count: number;
  include_hashtags: boolean;
  max_chars: number;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

const initialForm: FormState = {
  topic: "Build a realtime AI content generator with FastAPI, Next.js, SSE, and multiple AI providers",
  provider: "gemini",
  tone: "professional",
  audience: "software developers and startup founders",
  language: "English",
  count: 1,
  include_hashtags: true,
  max_chars: 280,
};

export default function Home() {
  const [form, setForm] = useState<FormState>(initialForm);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [content, setContent] = useState("");
  const [status, setStatus] = useState("Idle");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState("");
  const [optimizerArtifact, setOptimizerArtifact] = useState<OptimizerArtifact | null>(null);
  const [optimizerState, setOptimizerState] = useState<"loading" | "ready" | "empty" | "error">("loading");
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadOptimizerArtifact() {
      try {
        const response = await fetch(`${API_URL}/api/optimizer/latest`);
        if (!response.ok) {
          throw new Error("Failed to load optimizer artifact");
        }

        const data = await response.json();
        if (cancelled) return;

        if (!data.available) {
          setOptimizerArtifact(null);
          setOptimizerState("empty");
          return;
        }

        setOptimizerArtifact(data.artifact as OptimizerArtifact);
        setOptimizerState("ready");
      } catch {
        if (cancelled) return;
        setOptimizerState("error");
      }
    }

    void loadOptimizerArtifact();
    return () => {
      cancelled = true;
    };
  }, []);

  function updateForm<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function formatScore(score: number) {
    return score.toFixed(3);
  }

  function formatAspectLabel(label: string) {
    return label.replaceAll("_", " ");
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
      const payload: Record<string, unknown> = {
        topic: form.topic,
        provider: form.provider,
        language: form.language,
        count: form.count,
        include_hashtags: form.include_hashtags,
        max_chars: form.max_chars,
      };

      if (showAdvanced) {
        if (form.tone) {
          payload.tone = form.tone;
        }
        if (form.audience.trim()) {
          payload.audience = form.audience.trim();
        }
      }

      const sessionResponse = await fetch(`${API_URL}/api/twitter/sessions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
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
        setStatus(`Streaming from ${data.provider_label} (${data.model})`);
      });

      eventSource.addEventListener("token", (event) => {
        const data = JSON.parse(event.data);
        setContent((prev) => prev + data.token);
      });

      eventSource.addEventListener("final", (event) => {
        const data = JSON.parse(event.data);
        if (typeof data.content === "string" && data.content.trim()) {
          setContent(data.content);
        }
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
        <div className="badge">FastAPI + Next.js + SSE + Gemini/Groq/Ollama + DSPy/GEPA</div>
        <h1>Realtime Twitter Content Generator</h1>
        <p>
          This demo sends a POST request to FastAPI, opens an SSE connection with
          EventSource, and streams AI tokens back into the UI in realtime. You can
          switch between Gemini, Groq, and Ollama from the same interface. DSPy +
          GEPA files are included for offline prompt optimization.
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
              <label htmlFor="provider">Provider</label>
              <select
                id="provider"
                value={form.provider}
                onChange={(event) => updateForm("provider", event.target.value as Provider)}
              >
                <option value="gemini">Gemini</option>
                <option value="groq">Groq</option>
                <option value="ollama">Ollama</option>
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

          <button
            className="advanced-toggle"
            type="button"
            onClick={() => setShowAdvanced((prev) => !prev)}
          >
            {showAdvanced ? "Hide advanced options" : "Show advanced options"}
          </button>

          {!showAdvanced ? (
            <div className="note compact-note">
              Simple mode keeps <code>tone</code> and <code>audience</code> hidden so the draft
              feels more natural and follows the brief more closely.
            </div>
          ) : null}

          {showAdvanced ? (
            <>
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
            </>
          ) : null}

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
            API URL: {API_URL}. Configure <code>AI_PROVIDER</code> and the matching
            provider keys in <code>backend/.env</code>, then run <code>./start.sh</code>.
          </div>
          <div className="note">
            Ollama runs locally at <code>http://localhost:11434</code>. Make sure Ollama
            is running and the selected model is already pulled if you choose it.
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

      <section className="optimizer-section">
        <div className="optimizer-header">
          <div>
            <div className="badge">DSPy + GEPA Dashboard</div>
            <h2>Prompt Evaluation Snapshot</h2>
          </div>
          {optimizerState === "ready" && optimizerArtifact ? (
            <div className="status">
              <span className="dot live" />
              Optimized with {optimizerArtifact.model}
            </div>
          ) : null}
        </div>

        {optimizerState === "loading" ? (
          <div className="card note-card">Loading optimizer artifact...</div>
        ) : null}

        {optimizerState === "error" ? (
          <div className="card note-card">Could not load optimizer artifact yet.</div>
        ) : null}

        {optimizerState === "empty" ? (
          <div className="card note-card">
            Run <code>cd backend && .venv/bin/python scripts/optimize_gepa.py</code> first to generate a
            dashboard artifact.
          </div>
        ) : null}

        {optimizerState === "ready" && optimizerArtifact ? (
          <>
            <div className="optimizer-grid">
              <div className="card metric-card">
                <span className="metric-label">Baseline</span>
                <strong>{formatScore(optimizerArtifact.baseline_validation_score)}</strong>
              </div>
              <div className="card metric-card">
                <span className="metric-label">Optimized</span>
                <strong>{formatScore(optimizerArtifact.optimized_validation_score)}</strong>
              </div>
              <div className="card metric-card">
                <span className="metric-label">Delta</span>
                <strong className={optimizerArtifact.score_delta >= 0 ? "positive" : "negative"}>
                  {optimizerArtifact.score_delta >= 0 ? "+" : ""}
                  {formatScore(optimizerArtifact.score_delta)}
                </strong>
              </div>
            </div>

            <div className="optimizer-layout">
              <div className="card">
                <h3>Prompt Lama vs Baru</h3>
                <div className="prompt-panels">
                  <article className="prompt-card">
                    <span className="comparison-label">Prompt lama</span>
                    <pre>
                      {optimizerArtifact.prompt_versions?.baseline_runtime_prompt ||
                        "Belum ada data prompt baseline di artifact ini."}
                    </pre>
                  </article>
                  <article className="prompt-card">
                    <span className="comparison-label">Prompt baru</span>
                    <pre>
                      {optimizerArtifact.prompt_versions?.optimized_runtime_prompt ||
                        "Belum ada data prompt optimized di artifact ini."}
                    </pre>
                  </article>
                </div>

                <div className="prompt-panels compact">
                  <article className="prompt-card">
                    <span className="comparison-label">DSPy baseline</span>
                    <pre>
                      {optimizerArtifact.prompt_versions?.baseline_dspy_instructions ||
                        "Belum ada data instruksi DSPy baseline."}
                    </pre>
                  </article>
                  <article className="prompt-card">
                    <span className="comparison-label">DSPy optimized</span>
                    <pre>
                      {optimizerArtifact.prompt_versions?.optimized_dspy_instructions ||
                        "Belum ada data instruksi DSPy optimized."}
                    </pre>
                  </article>
                </div>

                {optimizerArtifact.prompt_change_summary?.length ? (
                  <div className="insight-list">
                    {optimizerArtifact.prompt_change_summary.map((item) => (
                      <p key={item}>{item}</p>
                    ))}
                  </div>
                ) : null}
              </div>

              <div className="card">
                <h3>Aspect Weights</h3>
                <div className="aspect-list">
                  {Object.entries(optimizerArtifact.score_weights).map(([key, value]) => (
                    <div className="aspect-row" key={key}>
                      <div>
                        <strong>{formatAspectLabel(key)}</strong>
                        <p>{optimizerArtifact.scoring_guide[key] || "No description available."}</p>
                      </div>
                      <span>{Math.round(value * 100)}%</span>
                    </div>
                  ))}
                </div>

                {optimizerArtifact.how_to_judge?.length ? (
                  <div className="insight-list">
                    {optimizerArtifact.how_to_judge.map((item) => (
                      <p key={item}>{item}</p>
                    ))}
                  </div>
                ) : null}
              </div>
            </div>

            <div className="optimizer-layout">
              <div className="card">
                <h3>Baseline vs Optimized</h3>
                <div className="comparison-list">
                  {optimizerArtifact.comparison_preview.map((comparison) => (
                    <article className="comparison-card" key={comparison.topic}>
                      <div className="comparison-top">
                        <h4>{comparison.topic}</h4>
                        <span className={comparison.score_delta >= 0 ? "positive" : "negative"}>
                          {comparison.score_delta >= 0 ? "+" : ""}
                          {formatScore(comparison.score_delta)}
                        </span>
                      </div>
                      <div className="score-pills">
                        <span className="score-pill">baseline: {formatScore(comparison.baseline_score)}</span>
                        <span className="score-pill">optimized: {formatScore(comparison.optimized_score)}</span>
                        {comparison.improved_aspects?.map((item) => (
                          <span className="score-pill positive" key={`${comparison.topic}-up-${item}`}>
                            better {formatAspectLabel(item)}
                          </span>
                        ))}
                        {comparison.weaker_aspects?.map((item) => (
                          <span className="score-pill negative" key={`${comparison.topic}-down-${item}`}>
                            weaker {formatAspectLabel(item)}
                          </span>
                        ))}
                      </div>
                      <div className="score-pills">
                        {Object.entries(comparison.aspect_delta).map(([key, value]) => (
                          <span
                            className={`score-pill ${value >= 0 ? "positive" : "negative"}`}
                            key={`${comparison.topic}-${key}`}
                          >
                            {formatAspectLabel(key)}: {value >= 0 ? "+" : ""}
                            {formatScore(value)}
                          </span>
                        ))}
                      </div>
                      <div className="comparison-columns">
                        <div>
                          <span className="comparison-label">Baseline</span>
                          <pre>{comparison.baseline_tweets}</pre>
                          {comparison.baseline_notes.length > 0 ? (
                            <p className="comparison-notes">{comparison.baseline_notes.join(" ")}</p>
                          ) : null}
                        </div>
                        <div>
                          <span className="comparison-label">Optimized</span>
                          <pre>{comparison.optimized_tweets}</pre>
                          {comparison.optimized_notes.length > 0 ? (
                            <p className="comparison-notes">{comparison.optimized_notes.join(" ")}</p>
                          ) : null}
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              </div>
            </div>

            <div className="optimizer-layout">
              <div className="card">
                <h3>Baseline Previews</h3>
                <div className="preview-list">
                  {optimizerArtifact.baseline_preview.map((preview) => (
                    <article className="preview-card" key={`baseline-${preview.topic}`}>
                      <div className="preview-top">
                        <h4>{preview.topic}</h4>
                        <span>{formatScore(preview.score)}</span>
                      </div>
                      <div className="score-pills">
                        {Object.entries(preview.aspect_scores).map(([key, value]) => (
                          <span className="score-pill" key={key}>
                            {key.replaceAll("_", " ")}: {formatScore(value)}
                          </span>
                        ))}
                      </div>
                      {preview.notes.length > 0 ? <p>{preview.notes.join(" ")}</p> : null}
                    </article>
                  ))}
                </div>
              </div>

              <div className="card">
                <h3>Optimized Previews</h3>
                <div className="preview-list">
                  {optimizerArtifact.optimized_preview.map((preview) => (
                    <article className="preview-card" key={`optimized-${preview.topic}`}>
                      <div className="preview-top">
                        <h4>{preview.topic}</h4>
                        <span>{formatScore(preview.score)}</span>
                      </div>
                      <div className="score-pills">
                        {Object.entries(preview.aspect_scores).map(([key, value]) => (
                          <span className="score-pill" key={key}>
                            {key.replaceAll("_", " ")}: {formatScore(value)}
                          </span>
                        ))}
                      </div>
                      {preview.notes.length > 0 ? <p>{preview.notes.join(" ")}</p> : null}
                    </article>
                  ))}
                </div>
              </div>
            </div>
          </>
        ) : null}
      </section>
    </main>
  );
}
