#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_PORT="${BACKEND_PORT:-8001}"
FRONTEND_PORT="${FRONTEND_PORT:-3001}"

cleanup() {
  echo ""
  echo "==> Stopping servers..."
  if [ -n "${BACKEND_PID:-}" ]; then kill "$BACKEND_PID" 2>/dev/null || true; fi
  if [ -n "${FRONTEND_PID:-}" ]; then kill "$FRONTEND_PID" 2>/dev/null || true; fi
}
trap cleanup EXIT INT TERM

cd "$BACKEND_DIR"

if [ ! -f ".env" ]; then
  echo "backend/.env not found. Run ./install.sh first, then add your KIMI_API_KEY."
  exit 1
fi

if [ -e ".venv-win/Scripts/python.exe" ]; then
  VENV_PYTHON=".venv-win/Scripts/python.exe"
elif [ -e ".venv/bin/python" ]; then
  VENV_PYTHON=".venv/bin/python"
elif [ -e ".venv/bin/python3" ]; then
  VENV_PYTHON=".venv/bin/python3"
elif [ -e ".venv/Scripts/python.exe" ]; then
  VENV_PYTHON=".venv/Scripts/python.exe"
else
  echo "Backend virtualenv not found for this shell."
  echo "If you are using Git Bash/Windows, create a Windows venv first."
  echo "If you are using WSL/Linux, run ./install.sh from that same shell."
  exit 1
fi

echo "==> Starting FastAPI backend on http://localhost:${BACKEND_PORT}"
FRONTEND_URL="http://localhost:${FRONTEND_PORT}" "$VENV_PYTHON" -m uvicorn app.main:app --reload --host 0.0.0.0 --port "$BACKEND_PORT" &
BACKEND_PID=$!

cd "$FRONTEND_DIR"

if [ -f ".next/dev/lock" ]; then
  LOCK_PID="$(sed -n 's/.*"pid":\([0-9][0-9]*\).*/\1/p' .next/dev/lock | head -n 1)"
  if [ -n "${LOCK_PID:-}" ] && ! cmd.exe /C "tasklist /FI \"PID eq ${LOCK_PID}\" | findstr ${LOCK_PID}" >/dev/null 2>&1; then
    rm -f .next/dev/lock
  fi
fi

echo "==> Starting Next.js frontend on http://localhost:${FRONTEND_PORT}"
if [ -f "node_modules/next/dist/bin/next" ]; then
  node "node_modules/next/dist/bin/next" dev --hostname 0.0.0.0 --port "$FRONTEND_PORT" &
else
  npm run dev -- --hostname 0.0.0.0 --port "$FRONTEND_PORT" &
fi
FRONTEND_PID=$!

echo ""
echo "==> Open http://localhost:${FRONTEND_PORT}"
echo "==> Backend docs http://localhost:${BACKEND_PORT}/docs"
echo "Press Ctrl+C to stop both servers."

wait
