# ----------------------------------------
# Base Image
# ----------------------------------------
FROM python:3.11-slim

# ----------------------------------------
# Environment Settings
# ----------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ----------------------------------------
# Set Workdir
# ----------------------------------------
WORKDIR /app

# ----------------------------------------
# Install pip and setuptools
# ----------------------------------------
RUN pip install --upgrade pip setuptools

# ----------------------------------------
# Copy Only Relevant Code
# ----------------------------------------
COPY dashboard/backend/pyproject.toml /app/pyproject.toml

# Install dependencies
RUN pip install .

# Now copy the rest of the backend code
COPY dashboard/backend /app

# ----------------------------------------
# Expose Port
# ----------------------------------------
EXPOSE 7000

# ----------------------------------------
# Startup Command
# ----------------------------------------
CMD ["uvicorn", "dashboard.backend.main:app", "--host", "0.0.0.0", "--port", "7000"]
