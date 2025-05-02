# Python
import psycopg2

connection = psycopg2.connect(
    user='postgres',
    password='fyukiAmane03!',
    host='localhost',
    port='5432',
    database='municipal_app'
)

create_statements = [
    ("users", """
        CREATE TABLE users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
    """),
    ("agencies", """
        CREATE TABLE agencies (
            agency_id SERIAL PRIMARY KEY,
            agency_name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT
        );
    """),
    ("town_councils", """
        CREATE TABLE town_councils (
            town_council_id SERIAL PRIMARY KEY,
            council_name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT
        );
    """),
    ("issue_types", """
        CREATE TABLE issue_types (
            issue_type_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT
        );
    """),
    ("issue_subcategories", """
        CREATE TABLE issue_subcategories (
            subcategory_id SERIAL PRIMARY KEY,
            issue_type_id INTEGER REFERENCES issue_types(issue_type_id) ON DELETE CASCADE,
            name VARCHAR(150) NOT NULL,
            description TEXT
        );
    """),
    ("jurisdictions", """
        CREATE TABLE jurisdictions (
            jurisdiction_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            geom GEOGRAPHY(POLYGON, 4326),
            town_council_id INTEGER REFERENCES town_councils(town_council_id)
        );
    """),
    ("issue_type_mappings", """
        CREATE TABLE issue_type_mappings (
            mapping_id SERIAL PRIMARY KEY,
            issue_type_id INTEGER REFERENCES issue_types(issue_type_id),
            jurisdiction_id INTEGER REFERENCES jurisdictions(jurisdiction_id),
            responsible_agency_id INTEGER REFERENCES agencies(agency_id),
            responsible_council_id INTEGER REFERENCES town_councils(town_council_id)
        );
    """),
    ("issues", """
        CREATE TABLE issues (
            issue_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
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
            town_council_id INTEGER REFERENCES town_councils(town_council_id),
            subzone_id INTEGER REFERENCES subzones(subzone_id),
            planning_area_id INTEGER REFERENCES planning_areas(planning_area_id),
            is_public BOOLEAN DEFAULT TRUE
        );
    """),
    ("forum_posts", """
        CREATE TABLE forum_posts (
            post_id SERIAL PRIMARY KEY,
            issue_id INTEGER REFERENCES issues(issue_id),
            user_id INTEGER REFERENCES users(user_id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """),
    ("comments", """
        CREATE TABLE comments (
            comment_id SERIAL PRIMARY KEY,
            post_id INTEGER REFERENCES forum_posts(post_id),
            user_id INTEGER REFERENCES users(user_id),
            parent_comment_id INTEGER REFERENCES comments(comment_id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """),
    ("post_votes", """
        CREATE TABLE post_votes (
            user_id INTEGER REFERENCES users(user_id),
            post_id INTEGER REFERENCES forum_posts(post_id),
            vote_type SMALLINT CHECK (vote_type IN (-1, 1)),
            PRIMARY KEY (user_id, post_id)
        );
    """),
    ("comment_votes", """
        CREATE TABLE comment_votes (
            user_id INTEGER REFERENCES users(user_id),
            comment_id INTEGER REFERENCES comments(comment_id),
            vote_type SMALLINT CHECK (vote_type IN (-1, 1)),
            PRIMARY KEY (user_id, comment_id)
        );
    """),
    ("media_assets", """
        CREATE TABLE media_assets (
            media_id SERIAL PRIMARY KEY,
            issue_id INTEGER REFERENCES issues(issue_id) ON DELETE CASCADE,
            media_type VARCHAR(20) CHECK (media_type IN ('image', 'video', 'audio')),
            file_path TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSONB
        );
    """),
    ("issue_status_history", """
        CREATE TABLE issue_status_history (
            history_id SERIAL PRIMARY KEY,
            issue_id INTEGER REFERENCES issues(issue_id) ON DELETE CASCADE,
            old_status VARCHAR(50),
            new_status VARCHAR(50) NOT NULL,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        );
    """),
    ("planning_areas", """
        CREATE TABLE planning_areas (
            planning_area_id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            geom GEOGRAPHY(MULTIPOLYGON, 4326) -- Optional: entire area boundary
        );
    """),
    ("subzones", """
        CREATE TABLE subzones (
            subzone_id SERIAL PRIMARY KEY,
            planning_area_id INTEGER REFERENCES planning_areas(planning_area_id),
            name VARCHAR(100) NOT NULL,
            geom GEOGRAPHY(MULTIPOLYGON, 4326) -- Spatial boundary of the subzone
        );
    """)
]   

try:
    with connection:
        with connection.cursor() as cursor:
            for table_name, create_sql in create_statements:
                cursor.execute(f'DROP TABLE IF EXISTS {table_name} CASCADE;')
                cursor.execute(create_sql)
    print("All tables dropped (if existed) and recreated successfully.")
except Exception as e:
    print("Error:", e)
finally:
    connection.close()