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
COPY api.py app.py main.py config.py /app/
COPY modules/ /app/modules/

EXPOSE 8000
CMD ["python", "main.py"]
