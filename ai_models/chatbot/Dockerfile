# --------------------------------------------------------
# Base image (Ubuntu + Ollama + Python)
# --------------------------------------------------------
FROM ubuntu:22.04

# --------------------------------------------------------
# Set environment variables
# --------------------------------------------------------
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# --------------------------------------------------------
# Set working directory
# --------------------------------------------------------
WORKDIR /app

# --------------------------------------------------------
# Install base system dependencies
# --------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ffmpeg libsndfile1 build-essential \
    python3.11 python3.11-venv python3.11-distutils python3-pip \
    ca-certificates gnupg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Symlink python3.11
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && ln -sf /usr/bin/pip3 /usr/bin/pip

# --------------------------------------------------------
# Install Ollama
# --------------------------------------------------------
RUN curl -fsSL https://ollama.com/install.sh | bash

# Confirm Ollama install
RUN ollama --version || true

# --------------------------------------------------------
# Copy application files & install dependencies 
# --------------------------------------------------------

# Copy only pyproject first (leverage Docker layer caching)
COPY ./ai_models/chatbot/pyproject.toml ./ai_models/chatbot/README.md /app/

# Install Python dependencies
RUN pip install --upgrade pip && pip install --default-timeout=300 .

# Copy rest of app
COPY ./config ./config
COPY ./ai_models/chatbot/app.py ./entrypoint.sh
COPY ./ai_models/chatbot/app.py ./app.py
COPY ./ai_models/chatbot/server.py ./server.py
COPY ./ai_models/chatbot/server.py ./save_cache.py
COPY ./ai_models/chatbot/models ./models

# --------------------------------------------------------
# Expose API Port
# --------------------------------------------------------
# EXPOSE 11434 # Not needed anymore as port :8100/ollama directs requests to Ollama API
EXPOSE 8100

# --------------------------------------------------------
# Entrypoint script
# --------------------------------------------------------
ENTRYPOINT ["/app/entrypoint.sh"]
