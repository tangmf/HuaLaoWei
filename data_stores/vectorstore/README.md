# Vectorstore (Weaviate)

This folder contains the setup and webhook handling logic for the **Weaviate** vector database.

## Components

- `setup.sh`  
  Shell script that:
  - Creates Weaviate collections/classes (e.g., Issue embeddings).
  - Optionally pre-seeds data from PostgreSQL issues table.
- `webhook_server/`  
  Lightweight Python Flask server that:
  - Listens for PostgreSQL trigger events via webhook.
  - Fetches updated issue details.
  - Embeds description text.
  - Upserts the vector and metadata into Weaviate.

- `Dockerfile.webhook`  
  Defines the webhook server container.

## Usage

1. Build and run `weaviate` service using Docker Compose.
2. Build and run `init_weaviate` service to create collections.
3. Build and run `vectorstore_webhook` service to start listening to events.

```bash
make setup-dev
make up
