#!/bin/sh
set -e

chmod +x /app/entrypoint.sh

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') [ENTRYPOINT] $1"
}

wait_for_server() {
  retries=30
  until curl -s http://localhost:11434/ > /dev/null; do
    retries=$((retries-1))
    if [ "$retries" -le 0 ]; then
      log "Error: Ollama server did not become ready in time."
      exit 1
    fi
    sleep 1
  done
}

log "Starting Ollama server..."
ollama serve &

log "Waiting for Ollama server to be ready..."
wait_for_server

log "Pulling Ollama models in background..."

log "Pulling model deepseek-r1:7b..."
ollama pull deepseek-r1:7b & pid1=$!

log "Pulling model deepseek-r1:14b..."
ollama pull deepseek-r1:14b & pid2=$!

log "Waiting for Ollama model pulls to finish..."
wait $pid1
wait $pid2

log "Saving chatbot service models into cache..."
python3 /app/save_cache.py --force

log "Starting chatbot FastAPI server..."
uvicorn app:app --host 0.0.0.0 --port 8100

wait
