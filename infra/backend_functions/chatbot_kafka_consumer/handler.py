import json
from chroma_updater import upsert_to_chroma

def handler(event, context):
    for record in event["records"]:
        try:
            payload = json.loads(record["value"])
            doc_id = payload["id"]
            content = payload["content"]
            metadata = payload.get("metadata", {})

            upsert_to_chroma(doc_id, content, metadata)

        except Exception as e:
            print(f"Failed to process record: {record}. Error: {e}")