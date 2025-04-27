FROM python:3.10-slim

WORKDIR /app

ENV ENV=dev

# System dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg libsndfile1 build-essential netcat-openbsd dos2unix && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# App source
COPY ./scripts /app/scripts/
# Convert the scripts to Unix line endings to ensure they run correctly on Linux:
RUN find /app/scripts -type f -name "*.sh" -exec dos2unix {} \;

COPY api.py app.py main.py config.py /app/
COPY modules/ /app/modules/

EXPOSE 8000
CMD ["python", "main.py"]
