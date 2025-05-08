# --------------------------------------------------------
# Base image (optimised for Transformers + Torch + CUDA)
# --------------------------------------------------------
FROM pytorch/pytorch:2.7.0-cuda11.8-cudnn9-runtime

# --------------------------------------------------------
# Set working directory
# --------------------------------------------------------
WORKDIR /app

# --------------------------------------------------------
# Install base system dependencies
# --------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------
# Copy application files & install dependencies 
# --------------------------------------------------------

# Copy only pyproject.toml and README.md first (leverage Docker layer caching)
COPY ./ai_models/vlm_issue_categoriser/pyproject.toml ./ai_models/vlm_issue_categoriser/README.md /app/

# Install Python dependencies
RUN pip install --upgrade pip && pip install --default-timeout=300 .

# Copy rest of app
COPY ./config ./config
COPY ./ai_models/vlm_issue_categoriser/app.py ./app.py
COPY ./ai_models/vlm_issue_categoriser/server.py ./server.py

# --------------------------------------------------------
# Expose ports
# --------------------------------------------------------
EXPOSE 8101

# --------------------------------------------------------
# Entrypoint
# --------------------------------------------------------
CMD ["python", "server.py"]
    
