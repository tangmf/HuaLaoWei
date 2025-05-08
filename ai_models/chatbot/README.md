# HuaLaoWei Chatbot Service

FastAPI server hosting core AI capabilities for the HuaLaoWei platform, including:

* Speech Transcription (Whisper tiny model)
* Text Translation (NLLB-200 distilled model)
* Text Embedding (MiniLM SentenceTransformer)
* Text Reranking (FlashRank model)
* Backed by Ollama server for large language model inference

Author: Fleming Siow
Date: 3rd May 2025

---

## Features

* **Speech-to-Text**: Transcribe user-uploaded audio files.
* **Translation**: Translate multilingual text into a target language.
* **Embeddings**: Generate dense embeddings for any text input.
* **Reranking**: Re-rank candidate documents based on relevance to a query.

---

## API Endpoints

| Endpoint      | Method | Description                               |
| ------------- | ------ | ----------------------------------------- |
| `/transcribe` | POST   | Transcribe audio input (UploadFile)       |
| `/translate`  | POST   | Translate text between languages          |
| `/embed`      | POST   | Generate embedding for a single text      |
| `/rerank`     | POST   | Rerank multiple documents against a query |

---

## Installation

### Requirements

* Python 3.9 or higher
* Ollama server (for LLM support)
* Docker (recommended for deployment)

### Local Setup (For Development)

```bash
# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install project dependencies
pip install .
```

You must also ensure an **Ollama server** is running locally:

```bash
ollama serve &
```

and that required models (e.g., `deepseek:7b`) are available.

---

## Running the Server

```bash
# Manually start Ollama if not started
ollama serve &

# Cache models if needed
python save_cache.py

# Launch FastAPI server
uvicorn app:app --host 0.0.0.0 --port 8005 --reload
```

---

## Docker Deployment

You can build and deploy the server easily using Docker:

```bash
# Build the Docker image
docker build -t hualaowei-chatbot .

# Run the container
docker run -p 11434:11434 -p 8100:8100 hualaowei-chatbot
docker run -p 11434:11434 -p 8100:8100 -v $(pwd)/ai_models/chatbot:/app hualaowei-chatbot
docker run -p 11434:11434 -p 8100:8100 -v %cd%/ai_models/chatbot:/app hualaowei-chatbot
docker run -p 11434:11434 -p 8100:8100 -v ${PWD}/ai_models/chatbot:/app hualaowei-chatbot

```

The container will:

* Start Ollama server
* Pull Ollama models (deepseek-r1:7b and deepseek-r1:14b)
* Cache HuggingFace models (Whisper, NLLB, MiniLM, FlashRank)
* Launch the FastAPI service automatically

---

## Model Caching

At container startup or manual setup, the system will:

* Check if models exist inside `/app/models`
* If missing, it will **download** and **cache**:

  * Whisper tiny (`openai/whisper-tiny`)
  * NLLB-200 distilled (`facebook/nllb-200-distilled-600M`)
  * MiniLM for embeddings (`sentence-transformers/all-MiniLM-L6-v2`)
  * FlashReranker (`ms-marco-MiniLM-L-12-v2`)

You can manually trigger model caching:

```bash
python save_cache.py --force
```

Cached models will be saved inside `/app/models`.

---

## Project Structure

```plaintext
/app
 ├── app.py             # Main FastAPI app (API endpoints)
 ├── server.py          # Uvicorn server launcher
 ├── save_cache.py      # HuggingFace model caching script
 ├── entrypoint.sh      # Full startup script including Ollama initialisation
 ├── healthcheck.sh     # Script to perform multiple healthchecks (for docker-compose)
 ├── pyproject.toml     # Project metadata and dependencies
 ├── README.md          # Documentation
 └── models/            # Downloaded models cache (Whisper, NLLB, MiniLM, FlashReranker)
```

---

## Notes on Ollama Integration

* Ollama serves LLM models (`deepseek-r1:7b` and `deepseek-r1:14b`) used for higher-order chatbot tasks.
* `save_cache.py` handles HuggingFace model caching separately.
* Ollama must be running for the chatbot to function properly.

---

## Useful Commands

```bash
docker login
docker tag hualaowei-chatbot flemingsiow/hualaowei-chatbot:latest
docker push flemingsiow/hualaowei-chatbot:latest

docker pull flemingsiow/hualaowei-chatbot:latest

```

---

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

## Acknowledgements

* Meta AI for the NLLB-200 translation model
* OpenAI for the Whisper speech recognition model
* Sentence-Transformers for MiniLM embeddings
* FlashRank team for reranking capabilities
* Ollama for efficient LLM management
* FastAPI for API server framework

---
