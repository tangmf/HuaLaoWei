FROM python:3.13-slim

WORKDIR /app

# Copy dependency file and install
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy .env code
COPY .env .

# Copy application code
COPY app.py .

# Expose port and start server
EXPOSE 5000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]