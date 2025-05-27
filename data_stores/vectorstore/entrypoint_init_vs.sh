#!/bin/bash
set -e

MAX_RETRIES=20
COUNT=0
until curl -sSf "$WEAVIATE_URL/v1/.well-known/ready" > /dev/null; do
  >&2 echo "Weaviate is unavailable at $WEAVIATE_URL - sleeping"
  sleep 2
  COUNT=$((COUNT + 1))
  if [ "$COUNT" -ge "$MAX_RETRIES" ]; then
    >&2 echo "Weaviate did not become ready after $MAX_RETRIES tries - exiting"
    exit 1
  fi
done

echo "Weaviate is up. Running vectorstore setup..."

# One-time vectorstore setup
python3 /app/data_stores/vectorstore/save_cache_init_vs.py
python3 /app/data_stores/vectorstore/setup_init_vs.py

echo "Vectorstore setup completed."

# Start the webhook server
echo "Starting Vectorstore Webhook Server..."
exec python3 /app/data_stores/vectorstore/webhook_init_vs.py
