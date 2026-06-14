# Kimi Twitter SSE Generator with FastAPI, Next.js, DSPy, and GEPA

A clean realtime demo for generating X/Twitter content using:

- **FastAPI** backend
- **Next.js** frontend
- **Server-Sent Events / SSE** realtime streaming
- **Kimi / Moonshot API** through the OpenAI-compatible API
- **DSPy + GEPA** folder and script for optional prompt optimization

This project is designed so you only need to paste your Kimi API key into `backend/.env`, then run the app.

---

## 1. Architecture

```txt
Next.js frontend
  │
  │ 1. POST /api/twitter/sessions
  │    body: topic, tone, audience, language, count...
  ▼
FastAPI backend
  │
  │ 2. Create temporary session_id
  ▼
Next.js frontend
  │
  │ 3. EventSource GET /api/twitter/sse/{session_id}
  ▼
FastAPI backend
  │
  │ 4. Call Kimi with stream=True
  │ 5. Yield each token as SSE event
  ▼
Next.js UI
  │
  │ 6. Append token to screen in realtime
```

Why this flow?

Browser `EventSource` is simple for SSE, but it opens a **GET** request. For real chat/generation forms, we usually need to send a larger **POST** body first. So the app uses:

```txt
POST first -> receive session_id -> GET SSE stream
```

---

## 2. Folder Structure

```txt
kimi-twitter-sse-dspy-gepa/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py          # env/settings
│   │   │   └── sse.py             # SSE event formatter
│   │   ├── models/
│   │   │   └── twitter.py         # Pydantic request/response models
│   │   ├── prompts/
│   │   │   ├── twitter/
│   │   │   │   ├── runtime.py     # runtime prompt builder
│   │   │   │   └── dspy.py        # DSPy signature/module/metric
│   │   ├── routers/
│   │   │   ├── health.py          # health endpoint
│   │   │   └── twitter.py         # session + SSE endpoints
│   │   ├── services/
│   │   │   ├── kimi_client.py     # Kimi OpenAI-compatible client
│   │   │   ├── session_store.py   # simple in-memory session storage
│   │   │   └── twitter_generator.py # generation service
│   │   └── main.py                # FastAPI app entry
│   ├── scripts/
│   │   └── optimize_gepa.py       # optional DSPy + GEPA optimizer
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx               # realtime UI
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── .env.example
│   └── package.json
├── docs/
│   └── architecture.md
├── install.sh
├── start.sh
└── README.md
```

---

## 3. Requirements

Make sure you have:

```bash
python --version
node --version
npm --version
```

Recommended:

```txt
Python 3.10+
Node.js 18+
npm 9+
```

For Windows Git Bash, the installer also tries:

```bash
py -3 --version
```

---

## 4. Install Step by Step

### Step 1 — unzip and enter the project

```bash
unzip kimi-twitter-sse-dspy-gepa.zip
cd kimi-twitter-sse-dspy-gepa
```

### Step 2 — allow scripts to run

```bash
chmod +x install.sh start.sh
```

### Step 3 — install backend and frontend dependencies

```bash
./install.sh
```

This will:

```txt
1. Create backend Python virtualenv
2. Install FastAPI, OpenAI SDK, DSPy, etc.
3. Install Next.js dependencies
4. Create backend/.env from backend/.env.example
5. Create frontend/.env.local from frontend/.env.example
```

---

## 5. Add Your Kimi API Key

Open:

```bash
backend/.env
```

Paste your token:

```env
KIMI_API_KEY=your_kimi_api_key_here
KIMI_BASE_URL=https://api.moonshot.ai/v1
KIMI_MODEL=kimi-k2.6
FRONTEND_URL=http://localhost:3000
```

Do not put `KIMI_API_KEY` in the frontend.

---

## 6. Start the App

From the root folder:

```bash
./start.sh
```

Open:

```txt
http://localhost:3000
```

Backend docs:

```txt
http://localhost:8000/docs
```

Health check:

```bash
curl http://localhost:8000/api/health
```

---

## 7. Test SSE From Terminal

Create a generation session:

```bash
curl -X POST "http://localhost:8000/api/twitter/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Realtime AI streaming with FastAPI and Next.js",
    "tone": "professional",
    "audience": "software developers",
    "language": "English",
    "count": 3,
    "include_hashtags": true,
    "max_chars": 280
  }'
```

You will get something like:

```json
{
  "session_id": "abc123",
  "sse_url": "/api/twitter/sse/abc123"
}
```

Then stream it:

```bash
curl -N "http://localhost:8000/api/twitter/sse/abc123"
```

The SSE response will look like:

```txt
event: start
data: {"message":"Twitter content generation started","model":"kimi-k2.6"}

event: token
data: {"token":"Tweet"}

event: token
data: {"token":" 1"}

event: done
data: {"done":true}
```

---

## 8. How the Frontend Works

File:

```txt
frontend/src/app/page.tsx
```

Main method:

```ts
const sessionResponse = await fetch(`${API_URL}/api/twitter/sessions`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(form),
});

const session = await sessionResponse.json();
const eventSource = new EventSource(`${API_URL}${session.sse_url}`);
```

Then each token is appended:

```ts
eventSource.addEventListener("token", (event) => {
  const data = JSON.parse(event.data);
  setContent((prev) => prev + data.token);
});
```

---

## 9. How the Backend Works

### Session endpoint

File:

```txt
backend/app/routers/twitter.py
```

Endpoint:

```txt
POST /api/twitter/sessions
```

It stores the request temporarily and returns a `session_id`.

### SSE endpoint

Endpoint:

```txt
GET /api/twitter/sse/{session_id}
```

It loads the request, calls Kimi with `stream=True`, and yields tokens as SSE.

### SSE formatter

File:

```txt
backend/app/core/sse.py
```

```py
def sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
```

The final `\n\n` is important. Without it, the browser may buffer and not emit the event.

---

## 10. DSPy + GEPA Explanation

DSPy + GEPA is included, but it is **not the realtime streaming method**.

Think of it like this:

```txt
SSE = realtime delivery method
Kimi = model that generates the text
DSPy = clean AI program abstraction
GEPA = offline optimizer to improve prompts/program quality
```

So the normal app can run immediately with your Kimi token.

GEPA is optional and should be run later when you want to improve the prompt.

---

## 11. Run Optional DSPy + GEPA Optimization

Make sure your app already works first.

### macOS/Linux/WSL

```bash
cd backend
source .venv/bin/activate
python scripts/optimize_gepa.py
```

### Windows Git Bash

```bash
cd backend
source .venv/Scripts/activate
python scripts/optimize_gepa.py
```

### Without activate

From root folder:

```bash
backend/.venv/bin/python backend/scripts/optimize_gepa.py
```

Windows Git Bash:

```bash
backend/.venv/Scripts/python.exe backend/scripts/optimize_gepa.py
```

The script saves:

```txt
backend/app/prompts/twitter/.generated/twitter_optimized_prompt.json
```

Runtime automatically loads this file through:

```txt
backend/app/prompts/twitter/runtime.py
```

Important: GEPA can call the LLM multiple times, so it may consume API credits.

---

## 12. Where to Edit Prompts

Runtime prompt:

```txt
backend/app/prompts/twitter/runtime.py
```

DSPy program:

```txt
backend/app/prompts/twitter/dspy.py
```

Optional GEPA script:

```txt
backend/scripts/optimize_gepa.py
```

---

## 13. Common Errors

### `KIMI_API_KEY is missing`

Fix:

```bash
nano backend/.env
```

Add:

```env
KIMI_API_KEY=your_token
```

### `.venv/bin/activate: No such file or directory`

On Windows Git Bash, use:

```bash
source backend/.venv/Scripts/activate
```

This project’s `start.sh` does not require activate, so normally you can just run:

```bash
./start.sh
```

### Microsoft Store Python alias issue

If Windows says Python is not found, install Python:

```powershell
winget install Python.Python.3.12
```

Then open a new terminal and run:

```bash
py -3 --version
```

---

## 14. Production Notes

For production, replace the in-memory session store with Redis or Postgres:

```txt
backend/app/services/session_store.py
```

Why?

The current store only works inside one backend process. If you deploy multiple instances, each instance has its own memory.

Also add:

```txt
- authentication
- rate limiting
- request logging without API keys
- content moderation / safety filters
- database persistence
- retry handling
- deployment env variables
```

---

## 15. GitHub Description

```txt
Realtime X/Twitter content generator using FastAPI, Next.js, Kimi API, SSE streaming, DSPy, and GEPA prompt optimization.
```
