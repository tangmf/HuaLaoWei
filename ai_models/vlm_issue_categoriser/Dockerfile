# --------------------------------------------------------
# Base Image: PyTorch 2.7 + CUDA 11.8 + cuDNN 9
# Optimised for HuggingFace Transformers and Torch
# --------------------------------------------------------
FROM pytorch/pytorch:2.7.0-cuda11.8-cudnn9-runtime

# --------------------------------------------------------
# Set Working Directory
# --------------------------------------------------------
WORKDIR /app

# --------------------------------------------------------
# Install System Dependencies
# --------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl && \
    rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------
# Python Dependency Installation
# --------------------------------------------------------

# Copy lockfiles first to enable Docker layer caching
COPY ./ai_models/vlm_issue_categoriser/pyproject.toml ./ai_models/vlm_issue_categoriser/README.md ./

RUN pip install --upgrade pip && pip install --default-timeout=300 .

# --------------------------------------------------------
# Copy Application Files
# --------------------------------------------------------
COPY ./config ./config
COPY ./ai_models/vlm_issue_categoriser/app.py ./app.py

# --------------------------------------------------------
# Expose API Port
# --------------------------------------------------------
EXPOSE 8101

# --------------------------------------------------------
# Start FastAPI Server
# --------------------------------------------------------
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8101"]
