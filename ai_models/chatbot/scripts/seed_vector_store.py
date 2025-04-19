# utils/seed_vector_store.py

import os
import argparse
import pandas as pd
import textwrap
import psycopg2
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()

MARKER_PATH = "./vector_stores/.vector_seeded"

parser = argparse.ArgumentParser()
parser.add_argument("--force", action="store_true", help="Force reseeding of vector store")
args = parser.parse_args()

if os.path.exists(MARKER_PATH) and not args.force:
    print("Vector store already seeded. Skipping seed_vector_store.py. Use --force to override.")
    exit(0)

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "host.docker.internal")
DB_PORT = os.getenv("DB_PORT")

CHROMA_PATH = "./vector_stores/chroma_store_textonly"

def fetch_issues(limit=500):
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    query = """
        SELECT issue_id, description, latitude, longitude,
               status, severity, full_address,
               (SELECT type_name FROM issue_types WHERE issue_type_id = i.issue_type_id) AS issue_type,
               (SELECT subtype_name FROM issue_subcategories WHERE subcategory_id = i.issue_subcategory_id) AS subcategory,
               (SELECT agency_name FROM agencies WHERE agency_id = i.agency_id) AS agency,
               datetime_reported
        FROM issues i
        ORDER BY datetime_reported DESC
        LIMIT %s
    """
    df = pd.read_sql(query, conn, params=(limit,))
    conn.close()
    return df

def format_issue_row(row):
    return textwrap.dedent(f"""\
        Description: {row.description}
        Location: {row.full_address} ({row.latitude:.4f}, {row.longitude:.4f})
        Reported on: {row.datetime_reported.strftime('%Y-%m-%d')}
        Severity: {row.severity}, Status: {row.status}
        Category: {row.issue_type} > {row.subcategory}
        Agency: {row.agency}
    """).strip()

def seed_vector_store():
    issues_df = fetch_issues()
    documents = [format_issue_row(row) for _, row in issues_df.iterrows()]
    metadata = [
        {
            "issue_id": int(row.issue_id),
            "agency": row.agency,
            "issue_type": row.issue_type,
            "subcategory": row.subcategory,
            "latitude": float(row.latitude),
            "longitude": float(row.longitude),
            "status": row.status,
            "severity": row.severity,
            "reported_on": row.datetime_reported.strftime("%Y-%m-%d"),
            "full_address": row.full_address,
        }
        for _, row in issues_df.iterrows()
    ]

    print("Encoding documents...")
    embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = embedder.encode(documents, show_progress_bar=True)
    embeddings = [e.tolist() for e in embeddings]

    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection("municipal_issues")

    ids = [f"issue_{meta['issue_id']}" for meta in metadata]

    print("Adding to ChromaDB...")
    collection.add(documents=documents, embeddings=embeddings, metadatas=metadata, ids=ids)

    os.makedirs(os.path.dirname(MARKER_PATH), exist_ok=True)
    with open(MARKER_PATH, "w") as f:
        f.write("done")
    print(f"Seeded {len(documents)} issues into ChromaDB.")

if __name__ == "__main__":
    seed_vector_store()
