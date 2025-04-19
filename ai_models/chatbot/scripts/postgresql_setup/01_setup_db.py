import os
import hashlib
import psycopg2
from faker import Faker
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load from .env
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def create_database_if_not_exists():
    # Connect to default 'postgres' db first
    con = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    # Check for existence
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    exists = cur.fetchone()

    if not exists:
        print(f"Creating database '{DB_NAME}'...")
        cur.execute(f"CREATE DATABASE {DB_NAME};")
    else:
        print(f"Database '{DB_NAME}' already exists.")

    cur.close()
    con.close()

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT    
    )

def create_reference_tables():
    conn = get_db_connection()
    cur = conn.cursor()

    # Create base tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS agencies (
        agency_id SERIAL PRIMARY KEY,
        agency_name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS issue_types (
        issue_type_id SERIAL PRIMARY KEY,
        type_name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS issue_subcategories (
        subcategory_id SERIAL PRIMARY KEY,
        issue_type_id INTEGER REFERENCES issue_types(issue_type_id),
        subtype_name TEXT NOT NULL
    );
    """)

    # Create issues table and enable PostGIS
    cur.execute("""
    CREATE EXTENSION IF NOT EXISTS postgis;

    CREATE TABLE IF NOT EXISTS issues (
        issue_id SERIAL PRIMARY KEY,
        user_id INTEGER,
        issue_type_id INTEGER REFERENCES issue_types(issue_type_id),
        issue_subcategory_id INTEGER REFERENCES issue_subcategories(subcategory_id),

        latitude DOUBLE PRECISION NOT NULL,
        longitude DOUBLE PRECISION NOT NULL,
        full_address TEXT,
        location GEOGRAPHY(Point, 4326),

        description TEXT,
        severity VARCHAR(50),
        status VARCHAR(50) DEFAULT 'Reported',
        datetime_reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        datetime_acknowledged TIMESTAMP,
        datetime_closed TIMESTAMP,
        datetime_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        agency_id INTEGER REFERENCES agencies(agency_id),
        town_council_id INTEGER,
        is_public BOOLEAN DEFAULT TRUE
    );
    """)

    # Populate agencies
    agencies = [
        "Building and Construction Authority (BCA)", "Housing and Development Board (HDB)",
        "Land Transport Authority (LTA)", "National Environment Agency (NEA)",
        "National Parks Board (NParks)", "People’s Association (PA)",
        "PUB, the National Water Agency", "Singapore Land Authority (SLA)",
        "Singapore Police Force (SPF)", "Urban Redevelopment Authority (URA)"
    ]

    for name in agencies:
        cur.execute("INSERT INTO agencies (agency_name) VALUES (%s) ON CONFLICT DO NOTHING", (name,))

    # Populate issue types and subcategories
    issue_map = {
        "Pests": [
            "Cockroaches in Food Establishment", "Mosquitoes", "Rodents in Common Areas",
            "Rodents in Food Establishment", "Bees & Hornets"
        ],
        "Animals & Bird": [
            "Dead Animal", "Injured Animal", "Bird Issues", "Cat Issues", "Dog Issues", "Other Animal Issues"
        ],
        "Smoking": [
            "Food Premises", "Parks & Park Connectors", "Other Public Areas"
        ],
        "Parks & Greenery": [
            "Fallen Tree/Branch", "Overgrown Grass", "Park Lighting Maintenance",
            "Park Facilities Maintenance", "Other Parks and Greenery Issues"
        ],
        "Drains & Sewers": [
            "Choked Drain/Stagnant Water", "Damaged Drain", "Flooding",
            "Sewer Choke/Overflow", "Sewage Smell"
        ],
        "Drinking Water": [
            "No Water", "Water Leak", "Water Pressure", "Water Quality"
        ],
        "Construction Sites": [
            "Construction Noise"
        ],
        "Abandoned Trolleys": [
            "Cold Storage", "Giant", "Mustafa", "FairPrice", "ShengSong", "Ikea"
        ],
        "Shared Bicycles": [
            "Anywheel", "HelloRide", "Others"
        ],
        "Others": ["Others"]
    }

    for issue_type, subcategories in issue_map.items():
        cur.execute("INSERT INTO issue_types (type_name) VALUES (%s) ON CONFLICT DO NOTHING RETURNING issue_type_id", (issue_type,))
        result = cur.fetchone()
        if not result:
            cur.execute("SELECT issue_type_id FROM issue_types WHERE type_name = %s", (issue_type,))
            result = cur.fetchone()
        issue_type_id = result[0]

        for subtype in subcategories:
            cur.execute("""
                INSERT INTO issue_subcategories (issue_type_id, subtype_name)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (issue_type_id, subtype))

    fake = Faker()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS town_councils (
        town_council_id SERIAL PRIMARY KEY,
        council_name VARCHAR(100) UNIQUE NOT NULL,
        description TEXT
    );
    """)

    # Pre-populate town councils
    town_council_names = [
        "Ang Mo Kio Town Council", "Bishan-Toa Payoh Town Council",
        "Chua Chu Kang Town Council", "East Coast Town Council",
        "Holland-Bukit Panjang Town Council", "Jalan Besar Town Council",
        "Jurong-Clementi Town Council", "Marine Parade Town Council",
        "Marsiling-Yew Tee Town Council", "Nee Soon Town Council",
        "Pasir Ris-Punggol Town Council", "Sembawang Town Council",
        "Tampines Town Council", "Tanjong Pagar Town Council",
        "West Coast Town Council"
    ]

    for name in town_council_names:
        cur.execute("""
            INSERT INTO town_councils (council_name, description)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (name, f"Administrative region managed by {name}"))

    # Generate fake users
    for _ in range(20):  # You can increase this number
        username = fake.user_name()
        email = fake.email()
        password_hash = hashlib.sha256(fake.password().encode()).hexdigest()
        last_login = fake.date_time_between(start_date='-10d', end_date='now')

        cur.execute("""
            INSERT INTO users (username, email, password_hash, last_login)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (username, email, password_hash, last_login))

    conn.commit()
    cur.close()
    conn.close()
    print("Reference data populated (users, agencies, town_councils, issue types, subcategories).")

if __name__ == "__main__":
    create_database_if_not_exists()
    create_reference_tables()
