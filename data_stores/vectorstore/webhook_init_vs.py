"""
webhook.py

FastAPI server to update the Vectorstore with sentence embeddings based on PostgreSQL issue records.

Author: Fleming Siow
Date: 5th May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import logging
import os
import uvicorn
import psycopg
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sentence_transformers import SentenceTransformer
from config.config import config

# --------------------------------------------------------
# Logger Setup
# --------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --------------------------------------------------------
# Configuration
# --------------------------------------------------------

ENV = config.env
VECTORSTORE_URL = config.data_stores.vectorstore.url
COLLECTION_NAME = config.data_stores.vectorstore.collection["issue"]["name"]

DB_CONFIG = config.data_stores.relational_db
DB_CONN_PARAMS = {
    "host": DB_CONFIG.host,
    "port": DB_CONFIG.port,
    "dbname": DB_CONFIG.database,
    "user": DB_CONFIG.user,
    "password": DB_CONFIG.password,
}

# --------------------------------------------------------
# Sentence Transformer Model
# --------------------------------------------------------

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# --------------------------------------------------------
# FastAPI App Setup
# --------------------------------------------------------

app = FastAPI()

# --------------------------------------------------------
# Helper Functions
# --------------------------------------------------------

def get_issue_details(issue_id: int):
    """
    Retrieves issue details from the database.
    """
    query = """SELECT i.issue_id, i.description, i.severity, i.address, i.status, sz.name AS subzone_name,
        i.datetime_reported, i.datetime_acknowledged, it.name AS issue_type, ist.name AS issue_subtype,
        a.name AS agency_name, tc.name AS town_council_name FROM issues i JOIN subzones sz ON i.subzone_id = sz.subzone_id
        JOIN issue_types it ON i.issue_type_id = it.issue_type_id JOIN issue_subtypes ist ON i.issue_subtype_id = ist.issue_subtype_id
        JOIN agencies a ON i.agency_id = a.agency_id JOIN town_councils tc ON i.town_council_id = tc.town_council_id
        WHERE i.description IS NOT NULL AND (i.status != 'Resolved' OR i.datetime_closed IS NULL) AND i.issue_id = %s
        ORDER BY i.datetime_updated ASC"""
    with psycopg.connect(**DB_CONN_PARAMS) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (issue_id,))
            return cursor.fetchone()

# --------------------------------------------------------
# API Endpoints
# --------------------------------------------------------

@app.post("/webhook/issue")
async def issue_webhook(request: Request):
    """
    Webhook endpoint to handle incoming issue updates and embed into the Vectorstore.
    """
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
            issue_type, issue_subtype, agency_name, town_council_name
        ) = issue

        vector = model.encode(description).tolist()

        combined_text = (
            f"Issue Type: {issue_type} > {issue_subtype}\n"
            f"Description: {description}\n"
            f"Severity: {severity}, Status: {status}\n"
            f"Location: {address or 'N/A'}, Subzone: {subzone_name}\n"
            f"Reported: {datetime_reported}\n"
            f"Acknowledged: {datetime_acknowledged}\n"
            f"Agency: {agency_name}, Town Council: {town_council_name}"
        )

        payload = {
            "class": COLLECTION_NAME,
            "id": str(issue_id),
            "properties": {
                "description": description,
                "severity": severity,
                "status": status,
                "address": address,
                "subzone": subzone_name,
                "issue_type": issue_type,
                "issue_subtype": issue_subtype,
                "agency": agency_name,
                "town_council": town_council_name,
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

# --------------------------------------------------------
# Entrypoint
# --------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("webhook:app", host="0.0.0.0", port=5005, reload=False)
