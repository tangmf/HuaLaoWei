import io
import mimetypes
from mobile_app.backend.data_stores.resources import Resources
from psycopg.rows import dict_row
from config.config import config

async def map_media_to_issue(resources: Resources, issue_id: int, media_type: str, file_path: str, metadata: dict | None = None):
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO issue_media_assets (issue_id, media_type, file_path, metadata) VALUES (%s, %s, %s, %s)",
                (issue_id, media_type, file_path, metadata)
            )

async def upload_file_to_os(resources: Resources, bucket_name: str, object_name: str, data: bytes) -> str: 
    stream = io.BytesIO(data)

    # Automatically detect content_type from object_name
    content_type, _ = mimetypes.guess_type(object_name)
    if content_type is None:
        content_type = "application/octet-stream"  # fallback if unknown

    resources.os_client.put_object(
        bucket_name,
        object_name,
        data=stream,  
        length=len(data),
        content_type=content_type
    )
    file_url = f"http://{resources.os_client._endpoint_url}/{bucket_name}/{object_name}"
    return file_url

async def delete_file_from_os(resources: Resources, bucket_name: str, object_name: str):
    resources.os_client.remove_object(bucket_name, object_name)
