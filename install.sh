#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

find_python() {
  if command -v python >/dev/null 2>&1 && python -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)' >/dev/null 2>&1; then
    echo "python"
    return 0
  fi

  if command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)' >/dev/null 2>&1; then
    echo "python3"
    return 0
  fi

  if command -v py >/dev/null 2>&1 && py -3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)' >/dev/null 2>&1; then
    echo "py -3"
    return 0
  fi

  return 1
}

PYTHON_CMD="$(find_python || true)"

if [ -z "$PYTHON_CMD" ]; then
  echo "Python 3.10+ not found."
  echo "Windows: install with: winget install Python.Python.3.12"
  echo "macOS: install with: brew install python"
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found. Install Node.js 18+ first: https://nodejs.org"
  exit 1
fi

echo "==> Using Python: $PYTHON_CMD"
echo "==> Installing backend dependencies..."
cd "$BACKEND_DIR"
# shellcheck disable=SC2086
$PYTHON_CMD -m venv .venv

if [ -x ".venv/bin/python" ]; then
  VENV_PYTHON=".venv/bin/python"
elif [ -x ".venv/Scripts/python.exe" ]; then
  VENV_PYTHON=".venv/Scripts/python.exe"
else
  echo "Could not find virtualenv Python executable."
  exit 1
fi

"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "==> Created backend/.env from backend/.env.example"
fi

echo "==> Installing frontend dependencies..."
cd "$FRONTEND_DIR"
npm install

if [ ! -f ".env.local" ]; then
  cp .env.example .env.local
  echo "==> Created frontend/.env.local from frontend/.env.example"
fi

echo ""
echo "==> Install complete."
echo "Next step: open backend/.env and configure AI_PROVIDER plus the matching provider credentials."
echo "Then run: ./start.sh"
