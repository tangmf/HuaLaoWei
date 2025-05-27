#!/bin/sh
set -e

# Wait for MinIO health check endpoint to be ready
MAX_RETRIES=30
RETRY_INTERVAL=3
RETRY_COUNT=0

# Configure MinIO client
mc alias set local "$MINIO_URL" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY"

# Create bucket if it does not already exist
if mc ls "local/$MINIO_BUCKET" > /dev/null 2>&1; then
  echo "Bucket $MINIO_BUCKET already exists. Skipping creation."
else
  echo "Creating bucket: $MINIO_BUCKET"
  mc mb "local/$MINIO_BUCKET"
fi

# Set the bucket policy to public read access
mc anonymous set public local/$MINIO_BUCKET

# Upload sample files if they exist
if [ -d app/data_stores/object_storage/sample_uploads ] && [ "$(ls -A app/data_stores/object_storage/sample_uploads)" ]; then
  echo "Uploading sample files to bucket $MINIO_BUCKET..."
  mc cp app/data_stores/object_storage/sample_uploads/* "local/$MINIO_BUCKET/" || echo "No files uploaded."
else
  echo "No sample files to upload."
fi

echo "Minio setup completed successfully."
