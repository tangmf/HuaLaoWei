import os
import psycopg2
import random
from faker import Faker
from dotenv import load_dotenv
from datetime import datetime, timedelta

fake = Faker()

# Load from .env
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def fetch_reference_ids():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT agency_id FROM agencies")
    agencies = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT subcategory_id, issue_type_id FROM issue_subcategories")
    subtypes = cur.fetchall()

    # Dummy user and town council IDs
    user_ids = list(range(1, 6))
    town_council_ids = list(range(1, 4))

    cur.close()
    conn.close()
    return agencies, subtypes, user_ids, town_council_ids

def insert_fake_issues(n=50):
    agencies, subtypes, user_ids, town_council_ids = fetch_reference_ids()
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        locations = [
            ("Jurong East MRT", 1.3331, 103.7420),
            ("Toa Payoh Central", 1.3321, 103.8478),
            ("Ang Mo Kio Hub", 1.3691, 103.8494),
            ("Bedok Reservoir", 1.3361, 103.9281),
        ]

        for _ in range(n):
            subcategory_id, issue_type_id = random.choice(subtypes)
            location_name, lat, lon = random.choice(locations)
            reported = fake.date_time_between(start_date='-10d', end_date='-1d')
            acknowledged = reported + timedelta(hours=random.randint(1, 24))
            closed = acknowledged + timedelta(hours=random.randint(1, 72))

            values = (
                random.choice(user_ids), issue_type_id, subcategory_id,
                lat, lon, location_name, lon, lat,
                fake.text(150), random.choice(["Low", "Medium", "High", "Critical"]),
                "Closed", reported, acknowledged, closed, datetime.now(),
                random.choice(agencies), random.choice(town_council_ids), random.choice([True, False])
            )

            cur.execute("""
                INSERT INTO issues (
                    user_id, issue_type_id, issue_subcategory_id,
                    latitude, longitude, full_address, location,
                    description, severity, status, datetime_reported,
                    datetime_acknowledged, datetime_closed, datetime_updated,
                    agency_id, town_council_id, is_public
                )
                VALUES (
                    %s, %s, %s,
                    %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s
                )
            """, values)

        if conn:
            conn.commit()
            print(f"Inserted {n} fake issues.")

    except Exception as e:
        print(f"Error during insert: {e}")

    finally:
        if cur and not cur.closed:
            cur.close()
        if conn and not conn.closed:
            conn.close()


if __name__ == "__main__":
    insert_fake_issues(n=200)
