"""
setup.py

Setup script for initializing vectorstore schema and embedding issues from relational database.

Author: Fleming Siow
Date: 5th May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import os, time, json, logging, requests, psycopg
from sentence_transformers import SentenceTransformer
from config.config import config

# --------------------------------------------------------
# Configuration and Constants
# --------------------------------------------------------

ENV = config.env
VECTORSTORE_URL = config.data_stores.vectorstore.url
COLLECTION_NAME = config.data_stores.vectorstore.collection["issue"]["name"]

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
            {"name": "issue_type", "dataType": ["text"]},
            {"name": "issue_subtype", "dataType": ["text"]},
            {"name": "agency", "dataType": ["text"]},
            {"name": "town_council", "dataType": ["text"]},
            {"name": "datetime_reported", "dataType": ["date"]},
            {"name": "datetime_acknowledged", "dataType": ["date"]},
            {"name": "combined_text", "dataType": ["text"]}
        ]
    }
    try:
        res = requests.post(f"{VECTORSTORE_URL}/v1/schema", json=schema)
        res.raise_for_status()
        logger.info("Collection '%s' created successfully.", COLLECTION_NAME)
    except requests.RequestException as e:
        logger.error("Failed to create schema: %s", e); raise

def embed_and_insert_issues():
    logger.info("Connecting to PostgreSQL database...")
    try:
        with psycopg.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD) as conn:
            with conn.cursor() as cursor:
                logger.info("Fetching issues from database...")
                cursor.execute("""
                    SELECT i.issue_id, i.description, i.severity, i.address, i.status, sz.name, 
                           i.datetime_reported, i.datetime_acknowledged, it.name, ist.name, 
                           a.name, tc.name
                    FROM issues i
                    JOIN subzones sz ON i.subzone_id = sz.subzone_id
                    JOIN issue_types it ON i.issue_type_id = it.issue_type_id
                    JOIN issue_subtypes ist ON i.issue_subtype_id = ist.issue_subtype_id
                    JOIN agencies a ON i.agency_id = a.agency_id
                    JOIN town_councils tc ON i.town_council_id = tc.town_council_id
                    WHERE i.description IS NOT NULL AND (i.status != 'Resolved' OR i.datetime_closed IS NULL)
                    ORDER BY i.datetime_updated ASC LIMIT 5000""")
                rows = cursor.fetchall()
    except Exception as e:
        logger.exception("Database query failed."); raise

    if not rows:
        logger.warning("No issues found to embed."); return

    batch = []
    logger.info("Embedding descriptions and preparing batch for insertion...")

    for row in rows:
        try:
            issue_id, description, severity, address, status, subzone_name, datetime_reported, datetime_acknowledged, issue_type, issue_subtype, agency_name, town_council_name = row
            vector = model.encode(description).tolist()
            combined_text = (f"Issue Type: {issue_type} > {issue_subtype}\nDescription: {description}\n"
                             f"Severity: {severity}, Status: {status}\nLocation: {address or 'N/A'}, Subzone: {subzone_name}\n"
                             f"Reported: {datetime_reported}\nAcknowledged: {datetime_acknowledged}\n"
                             f"Agency: {agency_name}, Town Council: {town_council_name}")
            batch.append({
                "class": COLLECTION_NAME,
                "id": str(issue_id),
                "properties": {
                    "description": description, "severity": severity, "status": status,
                    "address": address, "subzone": subzone_name, "issue_type": issue_type,
                    "issue_subtype": issue_subtype, "agency": agency_name, "town_council": town_council_name,
                    "datetime_reported": datetime_reported.isoformat() if datetime_reported else None,
                    "datetime_acknowledged": datetime_acknowledged.isoformat() if datetime_acknowledged else None,
                    "combined_text": combined_text
                },
                "vector": vector
            })
        except Exception as e:
            logger.warning("Failed to process issue ID %s: %s", issue_id, e)

    if batch:
        logger.info("Inserting %d objects into vectorstore...", len(batch))
        try:
            res = requests.post(f"{VECTORSTORE_URL}/v1/batch/objects", json={"objects": batch})
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
