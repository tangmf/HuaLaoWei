FROM python:3.10-slim

WORKDIR /app

ENV ENV=dev

# System dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg libsndfile1 build-essential netcat-openbsd && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# App source
COPY ./scripts /app/scripts/
COPY api.py app.py .env /app/
COPY modules/ /app/modules/

# Pre-cache models at build time
RUN python scripts/save_cache.py

# Expose the port the app runs on
EXPOSE 9000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "9000"]
