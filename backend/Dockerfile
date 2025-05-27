# --------------------------------------------------------
# Base Image: Python 3.11 (Slim)
# Lightweight base for FastAPI + Uvicorn backend
# --------------------------------------------------------
FROM python:3.11-slim

# --------------------------------------------------------
# Install system dependencies for psycopg
# --------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
 && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------
# Environment Variables
# --------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# --------------------------------------------------------
# Set Working Directory
# --------------------------------------------------------
WORKDIR /app

# --------------------------------------------------------
# Install Python Dependencies
# --------------------------------------------------------

# Copy lockfiles early for better layer caching
COPY ./backend/pyproject.toml ./backend/README.md ./

# Make sure psycopg[pool] is in your pyproject.toml
RUN pip install --upgrade pip \
 && pip install --default-timeout=300 .

# --------------------------------------------------------
# Copy Application Code
# --------------------------------------------------------
COPY ./config ./config
COPY ./backend ./backend

# --------------------------------------------------------
# Expose API Port
# --------------------------------------------------------
EXPOSE 8000

# --------------------------------------------------------
# Start Uvicorn Server (FastAPI)
# --------------------------------------------------------
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
