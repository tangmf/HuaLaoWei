#!/bin/sh
set -e

echo "[ENTRYPOINT] Starting Ollama server..."
ollama serve &

# Wait for the Ollama server to be ready (give it a few seconds)
echo "[ENTRYPOINT] Waiting for server to come up..."
sleep 10

echo "[ENTRYPOINT] Pulling model mistral:7b..."
ollama pull mistral:7b

echo "[ENTRYPOINT] Pulling model deepseek-r1:7b..."
ollama pull deepseek-r1:7b

# Wait for server to keep running
wait
 