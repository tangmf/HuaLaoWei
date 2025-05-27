"""
setup.py

Setup script for initializing vectorstore schema and embedding issues from relational database.

Author: Fleming Siow
Date: 5th May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import uuid
import os, time, json, logging, requests, psycopg
from sentence_transformers import SentenceTransformer
from config.config import config

# --------------------------------------------------------
# Configuration and Constants
# --------------------------------------------------------

ENV = config.env
VECTORSTORE_URL = config.data_stores.vectorstore.url
COLLECTION_NAME = config.data_stores.vectorstore.collection["issue"].name

DB_CONFIG = config.data_stores.relational_db
DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD = DB_CONFIG.host, DB_CONFIG.port, DB_CONFIG.database, DB_CONFIG.user, DB_CONFIG.password

# --------------------------------------------------------
# Logger Setup
# --------------------------------------------------------

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------------
# Model Initialisation
# --------------------------------------------------------

try:
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
except Exception as e:
    logger.exception("Failed to load SentenceTransformer model."); raise

# --------------------------------------------------------
# Functions
# --------------------------------------------------------

def wait_for_weaviate(max_retries=10, delay=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{VECTORSTORE_URL}/v1/.well-known/ready", timeout=5)
            if response.status_code == 200:
                logger.info("Weaviate is ready."); return
        except Exception:
            logger.info("Waiting for Weaviate to be ready (attempt %d/%d)...", attempt + 1, max_retries)
        time.sleep(delay)
    logger.critical("Weaviate not reachable after %d attempts.", max_retries)
    raise ConnectionError("Failed to connect to Weaviate.")

def create_schema_if_not_exists():
    logger.info("Checking if collection '%s' exists...", COLLECTION_NAME)
    try:
        response = requests.get(f"{VECTORSTORE_URL}/v1/schema/{COLLECTION_NAME}")
        if response.status_code == 200:
            logger.info("Collection '%s' already exists.", COLLECTION_NAME); return
        elif response.status_code != 404:
            response.raise_for_status()
    except requests.RequestException as e:
        logger.error("Error checking schema existence: %s", e); raise

    schema = {
        "class": COLLECTION_NAME,
        "vectorizer": "none",
        "properties": [
            {"name": "description", "dataType": ["text"]},
            {"name": "severity", "dataType": ["text"]},
            {"name": "status", "dataType": ["text"]},
            {"name": "address", "dataType": ["text"]},
            {"name": "subzone", "dataType": ["text"]},
            {"name": "issue_type", "dataType": ["text[]"]},
            {"name": "issue_subtype", "dataType": ["text[]"]},
            {"name": "agency", "dataType": ["text"]},
            {"name": "town_council", "dataType": ["text"]},
            {"name": "datetime_reported", "dataType": ["date"]},
            {"name": "datetime_acknowledged", "dataType": ["date"]},
            {"name": "combined_text", "dataType": ["text"]}
        ]
    }
    try:
        res = requests.post(f"{VECTORSTORE_URL}/v1/schema", json=schema)
        if res.status_code != 200:
            logger.error("Weaviate error response: %s", res.text)
            res.raise_for_status()
        logger.info("Collection '%s' created successfully.", COLLECTION_NAME)
    except requests.RequestException as e:
        logger.error("Failed to create schema: %s", e); raise
    
def safe_iso(dt):
    return dt.isoformat() if dt else None

def safe_text(value):
    return value if value is not None else ""

def embed_and_insert_issues():
    logger.info("Connecting to PostgreSQL database...")
    try:
        with psycopg.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD) as conn:
            with conn.cursor() as cursor:
                logger.info("Fetching issues from database...")
                cursor.execute("""
                    SELECT 
                        i.issue_id,
                        i.description,
                        i.severity,
                        i.address,
                        i.status,
                        sz.name AS subzone_name,
                        i.datetime_reported,
                        i.datetime_acknowledged,
                        ARRAY_AGG(DISTINCT it.name) AS issue_types,
                        ARRAY_AGG(DISTINCT ist.name) AS issue_subtypes,
                        a.name AS agency_name,
                        tc.name AS town_council_name
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
                    GROUP BY i.issue_id, i.description, i.severity, i.address, i.status,
                            sz.name, i.datetime_reported, i.datetime_acknowledged,
                            a.name, tc.name
                    ORDER BY i.datetime_updated ASC
                    LIMIT 5000;
                """)
                rows = cursor.fetchall()
    except Exception as e:
        logger.exception("Database query failed."); raise

    if not rows:
        logger.warning("No issues found to embed."); return

    batch = []
    logger.info("Embedding descriptions and preparing batch for insertion...")

    for row in rows:
        try:
            (issue_id, description, severity, address, status, subzone_name,
            datetime_reported, datetime_acknowledged, issue_types, issue_subtypes,
            agency_name, town_council_name) = row
            vector = model.encode(description).tolist()
            combined_text = (f"Issue Type(s): {', '.join(issue_types or [])}\n"
                 f"Issue Subtype(s): {', '.join(issue_subtypes or [])}\n"
                 f"Description: {description}\n"
                 f"Severity: {severity}, Status: {status}\n"
                 f"Location: {address or 'N/A'}, Subzone: {subzone_name}\n"
                 f"Reported: {datetime_reported}\nAcknowledged: {datetime_acknowledged}\n"
                 f"Agency: {agency_name}, Town Council: {town_council_name}")
            batch.append({
                "class": COLLECTION_NAME,
                "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"issue:{issue_id}")),
                "properties": {
                    "description": safe_text(description),
                    "severity": safe_text(severity),
                    "status": safe_text(status),
                    "address": safe_text(address),
                    "subzone": safe_text(subzone_name),
                    "issue_type": [safe_text(t) for t in issue_types if t],
                    "issue_subtype": [safe_text(s) for s in issue_subtypes if s],
                    "agency": safe_text(agency_name),
                    "town_council": safe_text(town_council_name),
                    "datetime_reported": safe_iso(datetime_reported),
                    "datetime_acknowledged": safe_iso(datetime_acknowledged),
                    "combined_text": safe_text(combined_text)
                },
                "vector": vector
            })
        except Exception as e:
            logger.warning("Failed to process issue ID %s: %s", issue_id, e)

    if batch:
        logger.info("Inserting %d objects into vectorstore...", len(batch))
        try:
            res = requests.post(f"{VECTORSTORE_URL}/v1/batch/objects", json={"objects": batch})
            if res.status_code != 200:
                logger.error("Weaviate response: %s", res.text)
                res.raise_for_status()
            logger.info("Successfully inserted %d issues.", len(batch))
        except requests.RequestException as e:
            logger.error("Batch insertion failed: %s", e); raise

def main():
    start_time = time.time()
    try:
        wait_for_weaviate()
        create_schema_if_not_exists()
        embed_and_insert_issues()
    except Exception as e:
        logger.critical("Setup failed: %s", e)
    else:
        logger.info("Setup completed successfully.")
    finally:
        logger.info("Elapsed time: %.2f seconds.", time.time() - start_time)

# --------------------------------------------------------
# Entry Point
# --------------------------------------------------------

if __name__ == "__main__":
    main()
