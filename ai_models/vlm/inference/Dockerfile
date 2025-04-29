# Base image with CUDA for GPU
FROM pytorch/pytorch:2.7.0-cuda11.8-cudnn9-runtime

# Create app directory
WORKDIR /app

# Copy dependency file and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Copy helper scripts
COPY helper.py .

# Expose port and start server
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
