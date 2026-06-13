#!/usr/bin/env bash
set -euo pipefail

OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required to start Ollama with this script."
  exit 1
fi

if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama is not installed. Install it first."
  exit 1
fi

echo "==> Starting Ollama service..."
brew services start ollama >/dev/null

echo "==> Waiting for Ollama at ${OLLAMA_URL} ..."
for _ in $(seq 1 20); do
  if curl -fsS "${OLLAMA_URL}/api/tags" >/dev/null 2>&1; then
    echo "==> Ollama is ready."
    echo "==> Models:"
    ollama list
    exit 0
  fi
  sleep 1
done

echo "Ollama service started, but the local API is not responding yet."
echo "Check logs with: brew services list"
exit 1
