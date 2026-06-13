#!/usr/bin/env bash
set -euo pipefail

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required to stop Ollama with this script."
  exit 1
fi

echo "==> Stopping Ollama service..."
brew services stop ollama >/dev/null
echo "==> Ollama stopped."
