# --------------------------------------------------------
# Base Image with Ubuntu 22.04 + Python 3.11 + Ollama
# --------------------------------------------------------
FROM ubuntu:22.04

# --------------------------------------------------------
# Environment Configuration
# --------------------------------------------------------
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# --------------------------------------------------------
# Set Working Directory
# --------------------------------------------------------
WORKDIR /app

# --------------------------------------------------------
# Install System Dependencies and Python 3.11
# --------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ffmpeg libsndfile1 build-essential \
    python3.11 python3.11-venv python3.11-distutils python3-pip \
    ca-certificates gnupg && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/pip3 /usr/bin/pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------
# Install Ollama for Model Execution
# --------------------------------------------------------
RUN curl -fsSL https://ollama.com/install.sh | bash

# Confirm Ollama installation (non-blocking)
RUN ollama --version || true

# --------------------------------------------------------
# Python Dependencies Setup
# --------------------------------------------------------

# Copy lock files early to leverage Docker cache
COPY ./ai_models/chatbot/pyproject.toml ./ai_models/chatbot/README.md ./

# Install Python dependencies (from current folder)
RUN pip install --upgrade pip && pip install --default-timeout=300 .

# --------------------------------------------------------
# Copy Remaining Application Files
# --------------------------------------------------------
COPY ./config ./config
COPY ./ai_models/chatbot/entrypoint.sh ./entrypoint.sh
COPY ./ai_models/chatbot/app.py ./app.py
COPY ./ai_models/chatbot/save_cache.py ./save_cache.py
COPY ./ai_models/chatbot/models ./models

# --------------------------------------------------------
# Expose API Port
# --------------------------------------------------------
EXPOSE 8100

# --------------------------------------------------------
# Define Entrypoint Script
# --------------------------------------------------------
ENTRYPOINT ["/app/entrypoint.sh"]
