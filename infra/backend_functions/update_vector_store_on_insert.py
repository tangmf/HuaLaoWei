import json
from modules.indexer import ChatbotIndexer
from sentence_transformers import SentenceTransformer

# Use shared embedder
embedder = SentenceTransformer("./models/sentence_model")

def handler(event, context):
    # Parse DB insert event (assumes payload structure)
    payload = json.loads(event['body'])
    issue_id = payload.get("issue_id")
    description = payload.get("description", "")
    metadata = {
        "latitude": payload.get("latitude"),
        "longitude": payload.get("longitude"),
        "severity": payload.get("severity"),
        "agency": payload.get("agency"),
        "town": payload.get("town"),
        "datetime": payload.get("datetime_reported"),
    }

    if not issue_id or not description:
        return {
            "statusCode": 400,
            "body": "Missing required fields"
        }

    indexer = ChatbotIndexer()
    embedding = embedder.encode(description).tolist()
    indexer.collection.upsert(
        ids=[f"issue-{issue_id}"],
        documents=[description],
        embeddings=[embedding],
        metadatas=[metadata]
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"Issue {issue_id} indexed successfully."})
    }
