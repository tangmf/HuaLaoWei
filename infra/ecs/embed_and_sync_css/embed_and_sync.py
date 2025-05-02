import os
import time
import json
import psycopg2
import requests
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
PGHOST = os.getenv("PGHOST")
PGPORT = os.getenv("PGPORT")
PGDATABASE = os.getenv("PGDATABASE")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")
PGSSL = os.getenv("PGSSL", "false").lower() == "true"
CSS_ENDPOINT = os.getenv("CSS_ENDPOINT").rstrip('/')

# Load model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=PGHOST,
    port=PGPORT,
    database=PGDATABASE,
    user=PGUSER,
    password=PGPASSWORD,
    sslmode="require" if PGSSL else "disable"
)
cursor = conn.cursor()

def embed_and_sync():
    print("Fetching issues without embedding...")
    cursor.execute("""
        SELECT
            i.issue_id, i.description, i.severity, i.address, i.status, sz.name AS subzone_name, 
            i.datetime_reported, i.datetime_acknowledged, 
            it.name AS issue_type, ist.name AS issue_subtype, a.name AS agency_name, tc.name AS town_council_name
        FROM issues i
        JOIN subzones sz ON i.subzone_id = sz.subzone_id
        JOIN issue_types it ON i.issue_type_id = it.issue_type_id
        JOIN issue_subtypes ist ON i.issue_subtype_id = ist.issue_subtype_id
        JOIN agencies a ON i.agency_id = a.agency_id
        JOIN town_councils tc ON i.town_council_id = tc.town_council_id
        WHERE i.description IS NOT NULL
            AND (i.status != 'Resolved' OR i.datetime_closed IS NULL)
        ORDER BY i.datetime_updated ASC
        LIMIT 1000;
    """)

    rows = cursor.fetchall()
    if not rows:
        print("No new issues to embed.")
        return

    print(f"Embedding {len(rows)} issue descriptions...")
    print(f"Embedding {len(rows)} issue descriptions...")
    for row in rows:
        (
            issue_id,
            description,
            severity,
            address,
            status,
            subzone_name,
            datetime_reported,
            datetime_acknowledged,
            issue_type,
            issue_subtype,
            agency_name,
            town_council_name
        ) = row

        try:
            vector = model.encode(description).tolist()

            combined_text = (
                f"Issue Type: {issue_type} > {issue_subtype}\n"
                f"Description: {description}\n"
                f"Severity: {severity}, Status: {status}\n"
                f"Location: {address or 'N/A'}, Subzone: {subzone_name}\n"
                f"Reported: {datetime_reported.strftime('%Y-%m-%d %H:%M') if datetime_reported else 'Unknown'}\n"
                f"Acknowledged: {datetime_acknowledged.strftime('%Y-%m-%d %H:%M') if datetime_acknowledged else 'Pending'}\n"
                f"Agency: {agency_name}, Town Council: {town_council_name}"
            )

            payload = {
                "doc": {
                    "embedding": vector,
                    "issue_id": issue_id,
                    "description": description,
                    "severity": severity,
                    "status": status,
                    "address": address,
                    "subzone": subzone_name,
                    "datetime_reported": datetime_reported.isoformat() if datetime_reported else None,
                    "datetime_acknowledged": datetime_acknowledged.isoformat() if datetime_acknowledged else None,
                    "issue_type": issue_type,
                    "issue_subtype": issue_subtype,
                    "agency": agency_name,
                    "town_council": town_council_name,
                    "combined_text": combined_text
                },
                "upsert": {
                    "embedding": vector,
                    "issue_id": issue_id,
                    "description": description,
                    "severity": severity,
                    "status": status,
                    "address": address,
                    "subzone": subzone_name,
                    "datetime_reported": datetime_reported.isoformat() if datetime_reported else None,
                    "datetime_acknowledged": datetime_acknowledged.isoformat() if datetime_acknowledged else None,
                    "issue_type": issue_type,
                    "issue_subtype": issue_subtype,
                    "agency": agency_name,
                    "town_council": town_council_name,
                    "combined_text": combined_text
                }
            }

            url = f"{CSS_ENDPOINT}/issues/_update/{issue_id}"
            headers = {"Content-Type": "application/json"}

            res = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
            if res.status_code >= 400:
                print(f"Failed to update issue {issue_id}:", res.text)
            else:
                print(f"Embedded issue {issue_id}")

        except Exception as e:
            print(f"Error embedding issue {issue_id}:", e)


if __name__ == "__main__":
    while True:
        embed_and_sync()
        time.sleep(10)
