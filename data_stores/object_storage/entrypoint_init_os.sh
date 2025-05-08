#!/bin/sh
set -e

# Print loaded environment
echo "Loaded environment settings:"
echo "OS_PROVIDER=${OS_PROVIDER:-Object Storage}"
echo "OS_URL=$OS_URL"
echo "OS_ACCESS_KEY=$OS_ACCESS_KEY"
echo "OS_SECRET_KEY=$OS_SECRET_KEY"
echo "OS_BUCKET=$OS_BUCKET"

# Validate critical environment variables
: "${OS_URL:?Environment variable OS_URL must be set}"
: "${OS_ACCESS_KEY:?Environment variable OS_ACCESS_KEY must be set}"
: "${OS_SECRET_KEY:?Environment variable OS_SECRET_KEY must be set}"
: "${OS_BUCKET:?Environment variable OS_BUCKET must be set}"

# Fallback default
OS_PROVIDER="${OS_PROVIDER:-Object Storage}"

echo "Waiting for $OS_PROVIDER to be ready at $OS_URL..."

# Wait for MinIO health check endpoint to be ready
MAX_RETRIES=30
RETRY_INTERVAL=3
RETRY_COUNT=0

# Configure MinIO client
mc alias set local "$OS_URL" "$OS_ACCESS_KEY" "$OS_SECRET_KEY"

# Create bucket if it does not already exist
if mc ls "local/$OS_BUCKET" > /dev/null 2>&1; then
  echo "Bucket $OS_BUCKET already exists. Skipping creation."
else
  echo "Creating bucket: $OS_BUCKET"
  mc mb "local/$OS_BUCKET"
fi

# Upload sample files if they exist
if [ -d app/data_stores/object_storage/sample_uploads ] && [ "$(ls -A app/data_stores/object_storage/sample_uploads)" ]; then
  echo "Uploading sample files to bucket $OS_BUCKET..."
  mc cp app/data_stores/object_storage/sample_uploads/* "local/$OS_BUCKET/" || echo "No files uploaded."
else
  echo "No sample files to upload."
fi

echo "$OS_PROVIDER setup completed successfully."
