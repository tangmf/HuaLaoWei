# Municipal Services Chatbot

This project is a modular AI-powered chatbot designed to support citizen engagement and civic services reporting in smart cities. It includes voice input, multilingual understanding, document search via RAG, and structured municipal issue tracking with full Docker-based automation.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Quickstart](#quickstart)
- [Usage](#usage)
- [Development Notes](#development-notes)
- [Environment Variables](#environment-variables)
- [License](#license)

## Overview

Key capabilities include:

- Speech-to-text transcription via Whisper
- Intent classification (LLMs, Hybrid Embeddings)
- Multimodal document retrieval via vector search (ChromaDB)
- PostgreSQL with PostGIS support for spatial issues
- Persistent issue database with mock data generation
- FastAPI backend with full Docker and Ollama support

## Project Structure

```
chatbot/
├── api.py
├── app.py
├── main.py
├── config.py
├── data/
│   ├── assets/
│   ├── inputs/
│   ├── outputs/
│   ├── rag_sources/
│   └── train_val_data/
├── models/
├── modules/
├── notebooks/
├── scripts/
│   ├── postgresql_setup/
│   └── save_cache.py
├── vector_stores/
├── .env
├── Dockerfile
├── docker-compose.yml
├── Makefile
```

## Quickstart

### 1. Setup `.env`

```
ENV=dev
DB_NAME=municipaldb
DB_USER=municipaluser
DB_PASSWORD=municipalpass
DB_HOST=db
DB_PORT=5432
OLLAMA_API_BASE=http://ollama:11434
```

### 2. Start Services

```bash
docker-compose up --build
```
or if you have `make` installed:

```bash
make build
```

On first run, this will (on development):

- Wait for PostgreSQL
- Create DB schema and mock issues
- Populate ChromaDB
- Download required libraries and models
- Launch FastAPI at http://localhost:8000

## Usage

### API Server Access

Visit http://localhost:8000 or use curl/Postman.

## Development Notes

### Notebooks

### Vector Store

- Stored in `vector_stores/` via ChromaDB
- Populated with `scripts/seed_vector_store.py`

### Model Caching

- `scripts/save_cache.py` downloads:
  - NLLB (translation)
  - Whisper (transcription)
  - MiniLM (embedding)
- Skipped if `.cache_complete` is found unless `--force`

### Database

- PostgreSQL with PostGIS
- `01_setup_db.py`: Creates tables
- `02_generate_issues.py`: Inserts mock data

## Environment Variables

| Variable         | Description                     |
|------------------|---------------------------------|
| ENV              | dev or test                     |
| DB_NAME          | PostgreSQL database name        |
| DB_USER          | Database username               |
| DB_PASSWORD      | Database password               |
| DB_HOST          | Hostname of the DB container    |
| DB_PORT          | PostgreSQL port (usually 5432)  |
| OLLAMA_API_BASE  | Ollama base URL (e.g. :11434)   |

## License
