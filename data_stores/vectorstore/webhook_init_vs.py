import logging
import os
import uuid
import uvicorn
import psycopg
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sentence_transformers import SentenceTransformer
from config.config import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ENV = config.env
VECTORSTORE_URL = config.data_stores.vectorstore.url
COLLECTION_NAME = config.data_stores.vectorstore.collection["issue"].name

DB_CONFIG = config.data_stores.relational_db
DB_CONN_PARAMS = {
    "host": DB_CONFIG.host,
    "port": DB_CONFIG.port,
    "dbname": DB_CONFIG.database,
    "user": DB_CONFIG.user,
    "password": DB_CONFIG.password,
}

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

app = FastAPI()

def get_issue_details(issue_id: int):
    query = """
    SELECT 
        i.issue_id, i.description, i.severity, i.address, i.status, sz.name AS subzone_name,
        i.datetime_reported, i.datetime_acknowledged, 
        ARRAY_AGG(DISTINCT it.name) AS issue_types,
        ARRAY_AGG(DISTINCT ist.name) AS issue_subtypes,
        a.name AS agency_name, tc.name AS town_council_name
    FROM issues i
    JOIN subzones sz ON i.subzone_id = sz.subzone_id
    LEFT JOIN issue_type_to_issue_mapping itim ON i.issue_id = itim.issue_id
    LEFT JOIN issue_types it ON itim.issue_type_id = it.issue_type_id
    LEFT JOIN issue_subtype_to_issue_mapping istim ON i.issue_id = istim.issue_id
    LEFT JOIN issue_subtypes ist ON istim.issue_subtype_id = ist.issue_subtype_id
    LEFT JOIN authorities auth ON i.authority_id = auth.authority_id
    LEFT JOIN agencies a ON auth.authority_type = 'agency' AND auth.authority_ref_id = a.agency_id
    LEFT JOIN town_councils tc ON auth.authority_type = 'town_council' AND auth.authority_ref_id = tc.town_council_id
    WHERE i.description IS NOT NULL 
    AND (i.status != 'Resolved' OR i.datetime_closed IS NULL) 
    AND i.issue_id = %s
    GROUP BY i.issue_id, sz.name, a.name, tc.name
    """

    with psycopg.connect(**DB_CONN_PARAMS) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (issue_id,))
            return cursor.fetchone()

@app.post("/webhook/issue")
async def issue_webhook(request: Request):
    try:
        data = await request.json()
        issue_id = data.get("issue_id")

        if not issue_id:
            return JSONResponse(content={"error": "Missing issue_id"}, status_code=400)

        issue = get_issue_details(issue_id)
        if not issue:
            return JSONResponse(content={"error": "Issue not found"}, status_code=404)

        (
            _issue_id, description, severity, address, status,
            subzone_name, datetime_reported, datetime_acknowledged,
            issue_types, issue_subtypes, agency_name, town_council_name
        ) = issue

        vector = model.encode(description).tolist()

        combined_text = (
            f"Issue Types: {', '.join(issue_types or [])} > {', '.join(issue_subtypes or [])}\n"
            f"Description: {description}\n"
            f"Severity: {severity}, Status: {status}\n"
            f"Location: {address or 'N/A'}, Subzone: {subzone_name}\n"
            f"Reported: {datetime_reported}\n"
            f"Acknowledged: {datetime_acknowledged}\n"
            f"Agency: {agency_name}, Town Council: {town_council_name}"
        )

        payload = {
            "class": COLLECTION_NAME,
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"issue:{issue_id}")),
            "properties": {
                "description": description or "",
                "severity": severity or "",
                "status": status or "",
                "address": address or "",
                "subzone": subzone_name or "",
                "issue_type": issue_types or [],
                "issue_subtype": issue_subtypes or [],
                "agency": agency_name or "",
                "town_council": town_council_name or "",
                "datetime_reported": datetime_reported.isoformat() if datetime_reported else None,
                "datetime_acknowledged": datetime_acknowledged.isoformat() if datetime_acknowledged else None,
                "combined_text": combined_text
            },
            "vector": vector
        }

        response = requests.post(f"{VECTORSTORE_URL}/v1/objects", json=payload)
        if response.status_code >= 400:
            logger.error(f"Failed to update vectorstore: {response.text}")
            return JSONResponse(content={"error": response.text}, status_code=500)

        return JSONResponse(content={"message": "Embedded and updated successfully."}, status_code=200)

    except Exception as e:
        logger.exception("Webhook processing failed.")
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("webhook_init_vs:app", host="0.0.0.0", port=5005, reload=False)
