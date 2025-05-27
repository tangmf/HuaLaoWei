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
# Python Dependencies Setup
# --------------------------------------------------------

# Copy lockfiles first to leverage Docker cache
COPY ./ai_models/stfm_issue_count/pyproject.toml ./ai_models/stfm_issue_count/README.md ./

# Install dependencies
RUN pip install --upgrade pip && pip install --default-timeout=300 .

# --------------------------------------------------------
# Copy Application Code
# --------------------------------------------------------
COPY ./config ./config
COPY ./ai_models/stfm_issue_count/app.py ./app.py
COPY ./ai_models/stfm_issue_count/models ./models

# --------------------------------------------------------
# Expose API Port
# --------------------------------------------------------
EXPOSE 8102

# --------------------------------------------------------
# Start FastAPI Server
# --------------------------------------------------------
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8102"]

