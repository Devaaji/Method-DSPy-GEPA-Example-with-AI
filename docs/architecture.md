# Architecture Notes

## Why POST + SSE?

Browser `EventSource` is designed around GET requests. A content generation form usually contains structured data: topic, tone, language, number of tweets, audience, etc. Passing all of that as a query string is not clean.

This project uses a two-step pattern:

```txt
POST /api/twitter/sessions
GET  /api/twitter/sse/{session_id}
```

The backend stores the POST payload temporarily and streams based on the session ID.

## Why keep Kimi in backend?

The Kimi API key must stay server-side. The browser only talks to your FastAPI backend. The frontend never receives or stores the model token.

## Why DSPy + GEPA is separate from SSE

DSPy + GEPA is useful for improving the AI program/prompt quality. SSE is only the delivery method for realtime output.

The runtime path is:

```txt
FastAPI router -> TwitterContentGenerator -> KimiClient -> stream tokens -> SSE
```

The optimization path is:

```txt
scripts/optimize_gepa.py -> DSPy TwitterContentProgram -> GEPA -> optimized_prompt.json
```

The runtime prompt loader checks if `optimized_prompt.json` exists. If yes, it uses that prompt. If not, it uses the default prompt.
