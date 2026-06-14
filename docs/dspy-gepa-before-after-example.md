# DSPy + GEPA Before/After Example

This file shows a concrete example of how the scoring flow works in this repo.

## Topic

`Building realtime AI streaming UI with FastAPI and Next.js`

## Before

```txt
Tweet 1: Unlock the power of AI with this revolutionary FastAPI and Next.js setup for realtime streaming. It is game-changing, seamless, and amazing for everyone building apps today! #AI #FastAPI #NextJS #Realtime
```

Why it is weak:

- Generic marketing words like `unlock`, `revolutionary`, `game-changing`, and `seamless`
- Too broad for the audience
- More hype than insight
- Too many hashtags

## After

```txt
Tweet 1: Most realtime AI demos feel smooth until the stream breaks under real user traffic.
Tweet 2: FastAPI handles the token stream well. Next.js makes the UI feel instant. The hard part is designing retries, loading states, and partial output that still feels trustworthy.
```

Why it is stronger:

- Opens with tension and a clearer hook
- Gives specific implementation insight
- Sounds more human and less generic
- Better fit for developers and founders

## How To Reproduce The Scores

Run:

```bash
cd backend
.venv/bin/python scripts/score_twitter_draft.py
```

This uses the same evaluator as GEPA in:

- [backend/app/prompts/scoring/evaluator.py](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/scoring/evaluator.py:1)
- [backend/app/prompts/twitter/dspy.py](/Users/devaajisaputra/Documents/Personal/Method-DSPy-GEPA-Example-with-AI/backend/app/prompts/twitter/dspy.py:1)

The output includes:

- `overall_score`
- `hook`
- `clarity`
- `relevance`
- `naturalness`
- `constraint_fit`
- `notes`

## How To Use This In Practice

1. Write a rough draft first.
2. Score it with the script.
3. Rewrite the weak areas shown in `notes`.
4. Compare the aspect scores.
5. Move good examples into the dataset files under `backend/app/prompts/datasets/`.
