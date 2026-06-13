#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_PORT="${BACKEND_PORT:-8001}"
FRONTEND_PORT="${FRONTEND_PORT:-3001}"

cd "$BACKEND_DIR"

if [ ! -f ".env" ]; then
  echo "backend/.env not found. Run ./install.sh first, then configure your provider settings."
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

cd "$FRONTEND_DIR"

if [ -f ".next/dev/lock" ]; then
  LOCK_PID="$(sed -n 's/.*"pid":\([0-9][0-9]*\).*/\1/p' .next/dev/lock | head -n 1)"
  if [ -n "${LOCK_PID:-}" ] && command -v cmd.exe >/dev/null 2>&1; then
    if ! cmd.exe /C "tasklist /FI \"PID eq ${LOCK_PID}\" | findstr ${LOCK_PID}" >/dev/null 2>&1; then
      rm -f .next/dev/lock
    fi
  fi
fi

cd "$ROOT_DIR"

if command -v concurrently >/dev/null 2>&1; then
  CONCURRENTLY_CMD="concurrently"
elif [ -x "$ROOT_DIR/frontend/node_modules/.bin/concurrently" ]; then
  CONCURRENTLY_CMD="$ROOT_DIR/frontend/node_modules/.bin/concurrently"
else
  echo "concurrently not found."
  echo "Install it first with one of these:"
  echo "  npm install -g concurrently"
  echo "  cd frontend && npm install --save-dev concurrently"
  exit 1
fi

echo "Starting all services..."
echo "Frontend: http://localhost:${FRONTEND_PORT}"
echo "Backend docs: http://localhost:${BACKEND_PORT}/docs"

"$CONCURRENTLY_CMD" \
  --prefix "[{name}]" \
  --names "backend,frontend" \
  --prefix-colors "yellow,green" \
  "cd \"$BACKEND_DIR\" && FRONTEND_URL=http://localhost:${FRONTEND_PORT} \"$VENV_PYTHON\" -m uvicorn app.main:app --reload --host 0.0.0.0 --port \"$BACKEND_PORT\"" \
  "cd \"$FRONTEND_DIR\" && npm run dev -- --hostname 0.0.0.0 --port \"$FRONTEND_PORT\""
