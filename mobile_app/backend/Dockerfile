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
# Install Hatch
# ----------------------------------------
RUN pip install --upgrade pip \
    && pip install hatch

# ----------------------------------------
# Copy Only Relevant Files
# ----------------------------------------
COPY mobile_app/backend/pyproject.toml /app/pyproject.toml

# Install dependencies
RUN hatch env create

# Now copy application code
COPY mobile_app/backend /app

# ----------------------------------------
# Expose Port
# ----------------------------------------
EXPOSE 8000

# ----------------------------------------
# Startup Command
# ----------------------------------------
CMD ["uvicorn", "mobile_app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
    