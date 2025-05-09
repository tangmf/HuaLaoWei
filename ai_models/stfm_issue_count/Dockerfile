# --------------------------------------------------------
# Base image (PyTorch + CUDA 11.8 runtime)
# --------------------------------------------------------
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

# --------------------------------------------------------
# Set working directory
# --------------------------------------------------------
WORKDIR /app

# --------------------------------------------------------
# Copy application files & install dependencies 
# --------------------------------------------------------

# Copy only pyproject.toml and README.md first (leverage Docker layer caching)
COPY ./ai_models/forecast_issue_count/pyproject.toml ./ai_models/forecast_issue_count/README.md /app/

# Install Python dependencies
RUN pip install --upgrade pip && pip install --default-timeout=300 .

# Copy rest of app
COPY ./config ./config
COPY ./ai_models/forecast_issue_count/app.py ./app.py
COPY ./ai_models/forecast_issue_count/server.py ./server.py
COPY ./ai_models/forecast_issue_count/models ./models

# --------------------------------------------------------
# Expose API Port
# --------------------------------------------------------
EXPOSE 8102

# --------------------------------------------------------
# Launch FastAPI server
# --------------------------------------------------------
CMD ["python", "server.py"]
