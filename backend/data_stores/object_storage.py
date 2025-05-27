from minio import Minio
from config.config import config

OS_CONFIG = config.data_stores.object_storage

os_client = Minio(
    endpoint=OS_CONFIG.endpoint,
    access_key=OS_CONFIG.access_key,
    secret_key=OS_CONFIG.secret_key,
    secure=False
)

# Create the bucket if it does not exist
if not os_client.bucket_exists(OS_CONFIG.bucket_name):
    os_client.make_bucket(OS_CONFIG.bucket_name)
