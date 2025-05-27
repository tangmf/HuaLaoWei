import os
import psycopg
import random
from faker import Faker
from shapely import wkb
from shapely.geometry import shape, Point
from config.config import config

def random_point_in_polygon(geom_geojson):
    polygon = shape(geom_geojson)
    minx, miny, maxx, maxy = polygon.bounds
    for _ in range(10):
        pnt = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if polygon.contains(pnt):
            return pnt.y, pnt.x  # latitude, longitude
    centroid = polygon.centroid
    return centroid.y, centroid.x

def main():

    print("Seeding issues table...")
    db_config = config.data_stores.relational_db
    db_params = {"host": db_config.host, "dbname": db_config.database, "user": db_config.user, "password": db_config.password}
    faker = Faker()
    statuses = ['Reported', 'Acknowledged', 'Resolved']
    severities = ['Low', 'Medium', 'High']
    singapore_streets = ["Ang Mo Kio Avenue 3", "Bedok North Road", "Tampines Street 11", "Clementi Avenue 2", "Jurong West Street 41", "Hougang Avenue 8", "Yishun Ring Road", "Pasir Ris Drive 6", "Bukit Timah Road", "Toa Payoh Lorong 6", "Woodlands Avenue 5", "Sengkang East Way", "Choa Chu Kang Avenue 3", "Serangoon Avenue 2", "Punggol Field", "Upper Thomson Road", "Telok Blangah Drive", "Jurong East Street 13", "Bishan Street 12", "Commonwealth Avenue"]

    with psycopg.connect(**db_params) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute('TRUNCATE TABLE issues RESTART IDENTITY CASCADE')
                print("Issues table truncated.")
                cursor.execute('TRUNCATE TABLE issue_type_to_issue_mapping RESTART IDENTITY CASCADE')
                cursor.execute('TRUNCATE TABLE issue_subtype_to_issue_mapping RESTART IDENTITY CASCADE')

                cursor.execute('SELECT user_id FROM users')
                users = [row[0] for row in cursor.fetchall()]

                cursor.execute('SELECT issue_type_id FROM issue_types')
                issue_types = [row[0] for row in cursor.fetchall()]

                cursor.execute('SELECT issue_subtype_id, issue_type_id FROM issue_subtypes')
                subtypes = cursor.fetchall()

                cursor.execute('SELECT agency_id FROM agencies')
                agencies = [row[0] for row in cursor.fetchall()]

                cursor.execute('SELECT town_council_id FROM town_councils')
                councils = [row[0] for row in cursor.fetchall()]

                cursor.execute('SELECT planning_area_id FROM planning_areas')
                planning_areas = [row[0] for row in cursor.fetchall()]

                cursor.execute('SELECT subzone_id, planning_area_id, ST_AsBinary(geom) FROM subzones')
                subzones_raw = cursor.fetchall()

                type_to_subtypes = {}
                for subtype_id, type_id in subtypes:
                    type_to_subtypes.setdefault(type_id, []).append(subtype_id)

                planning_area_to_subzones = {}
                for subzone_id, planning_id, geom_binary in subzones_raw:
                    try:
                        geom = wkb.loads(geom_binary)
                        planning_area_to_subzones.setdefault(planning_id, []).append((subzone_id, geom))
                    except Exception as e:
                        print(f"Invalid geom skipped: {e}")

                inserted_issue_ids = []

                for _ in range(5000):
                    user_id = random.choice(users)
                
                    if random.random() < 0.5:
                        authority_type = 'agency'
                        authority_ref_id = random.choice(agencies)
                    else:
                        authority_type = 'town_council'
                        authority_ref_id = random.choice(councils)

                    cursor.execute("""
                        SELECT authority_id FROM authorities
                        WHERE authority_type = %s AND authority_ref_id = %s
                        LIMIT 1
                    """, (authority_type, authority_ref_id))
                    result = cursor.fetchone()
                    if not result:
                        continue
                    authority_id = result[0]

                    planning_area_id = random.choice(planning_areas)
                    subzones = planning_area_to_subzones.get(planning_area_id)
                    if not subzones:
                        continue
                    subzone_id, geom = random.choice(subzones)
                    try:
                        latitude, longitude = random_point_in_polygon(geom)
                    except Exception:
                        continue
                    block_number = random.randint(1, 999)
                    use_block = random.choice([True, False])
                    address = f"Block {block_number} {random.choice(singapore_streets)}" if use_block else f"{block_number} {random.choice(singapore_streets)}"
                    severity = random.choice(severities)
                    status = random.choice(statuses)
                    datetime_reported = faker.date_time_between(start_date='-14d', end_date='now')
                    datetime_acknowledged = faker.date_time_between(start_date=datetime_reported, end_date='now')
                    if status == 'Resolved':
                        datetime_closed = faker.date_time_between(start_date=datetime_acknowledged, end_date='now')
                        datetime_updated = faker.date_time_between(start_date=datetime_closed, end_date='now')
                    else:
                        datetime_closed = None
                        datetime_updated = faker.date_time_between(start_date=datetime_acknowledged, end_date='now')
                    is_public = random.random() < 0.8
                    cursor.execute("""
                        INSERT INTO issues (
                            user_id, latitude, longitude, address, description, severity, status,
                            datetime_reported, datetime_acknowledged, datetime_closed, datetime_updated,
                            authority_id, planning_area_id, subzone_id, is_public
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING issue_id
                    """, (
                        user_id, latitude, longitude, 
                        address, f"Issue reported at {address}", severity, status,
                        datetime_reported, datetime_acknowledged, datetime_closed, datetime_updated,
                        authority_id, planning_area_id, subzone_id, is_public
                    ))
                    issue_id = cursor.fetchone()[0]
                    inserted_issue_ids.append(issue_id)

                    # Insert random type-subtype mappings
                    selected_types = random.sample(issue_types, k=random.randint(1, min(2, len(issue_types))))
                    for type_id in selected_types:
                        cursor.execute('INSERT INTO issue_type_to_issue_mapping (issue_id, issue_type_id) VALUES (%s, %s)', (issue_id, type_id))
                        subtype_ids = type_to_subtypes.get(type_id)
                        if subtype_ids:
                            selected_subtypes = random.sample(subtype_ids, k=random.randint(1, min(2, len(subtype_ids))))
                            for subtype_id in selected_subtypes:
                                cursor.execute('INSERT INTO issue_subtype_to_issue_mapping (issue_id, issue_subtype_id) VALUES (%s, %s)', (issue_id, subtype_id))

                print(f"Inserted {len(inserted_issue_ids)} issues successfully.")
            except Exception as e:
                print(f"Error seeding issues: {e}")
                raise

            print("Seeding issues done.")

            seed_media_assets(cursor, inserted_issue_ids)
            seed_forum_posts_and_comments(cursor, inserted_issue_ids, users)
    

ISSUE_TYPE_MEDIA_MAP = {
    1: [],
    2: [],
    3: [],
    4: [],
    5: ["Animals & Bird_Dead Animal_001.jpg", "Animals & Bird_Dog Issues_001.jpg"],
    6: ["Pests_Cockroaches in Food Establishment_001.jpg", "Pests_Rodents in Common Areas_001.jpg"],
    7: ["Parks & Greenery_Park Facilities Maintenance_001.jpg"],
    8: ["Smoking_Parks & Park Connectors_001.jpg", "Smoking_Food Premises_001.jpg"],
    9: ["Shared Bicycles_Anywhere_001.jpg", "Shared Bicycles_Others_001.jpg"],
    10: ["Abandoned Trolleys_Giant_001.jpg", "Abandoned Trolleys_FairPrice_001.jpg"],
    11: ["Drains & Sewers_Sewer Choke or Overflow_001.jpg", "Drains & Sewers_Damaged Drain_001.jpg"],
    12: ["Construction Sites_Construction Noise_001.jpg", "Construction Sites_Construction Noise_002.jpg"],
    13: ["Drinking Water_Water Quality_001.jpg", "Drinking Water_Water Leak_001.jpg"],
    14: ["Others_Miscellaneous_001.jpg", "Others_Miscellaneous_002.jpg"]
}
VALID_EXTENSIONS = {
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".gif": "image",
    ".mp4": "video",
    ".mp3": "audio",
    ".wav": "audio",
    ".pdf": "document"
}

def seed_media_assets(cursor, issue_ids):
    print("Seeding issue_media_assets (type-aware)...")

    # Build reverse lookup: issue_id > issue_type_ids
    cursor.execute("SELECT issue_id, issue_type_id FROM issue_type_to_issue_mapping")
    issue_type_links = cursor.fetchall()
    issue_type_dict = {}
    for issue_id, type_id in issue_type_links:
        issue_type_dict.setdefault(issue_id, []).append(type_id)

    inserted = 0
    for issue_id in issue_ids:
        type_ids = issue_type_dict.get(issue_id, [])
        if not type_ids:
            continue
        for type_id in type_ids:
            filenames = ISSUE_TYPE_MEDIA_MAP.get(type_id, [])
            if not filenames:
                continue
            selected_files = random.sample(filenames, k=min(2, len(filenames)))
            for filename in selected_files:
                ext = os.path.splitext(filename)[1].lower()
                media_type = VALID_EXTENSIONS.get(ext, "document")
                cursor.execute("""
                    INSERT INTO issue_media_assets (issue_id, media_type, file_path)
                    VALUES (%s, %s, %s)
                """, (issue_id, media_type, filename))
                inserted += 1

    print(f"Inserted {inserted} media assets (type-aware).")

def seed_forum_posts_and_comments(cursor, issue_ids, users):
    print("Seeding forum_posts, comments, votes...")
    post_ids = []
    comment_ids = []

    faker = Faker()

    for issue_id in issue_ids:
        if random.random() < 0.5:
            user_id = random.choice(users)
            title = f"Discussion about issue #{issue_id}"
            cursor.execute("""
                INSERT INTO forum_posts (issue_id, user_id, title)
                VALUES (%s, %s, %s) RETURNING post_id
            """, (issue_id, user_id, title))
            post_id = cursor.fetchone()[0]
            post_ids.append(post_id)

            # Comments
            for _ in range(random.randint(1, 3)):
                comment_user_id = random.choice(users)
                content = faker.sentence()
                cursor.execute("""
                    INSERT INTO comments (post_id, user_id, content)
                    VALUES (%s, %s, %s) RETURNING comment_id
                """, (post_id, comment_user_id, content))
                comment_id = cursor.fetchone()[0]
                comment_ids.append(comment_id)

    # Post Votes
    for post_id in post_ids:
        for _ in range(random.randint(1, 5)):
            voter_id = random.choice(users)
            vote_type = random.choice([-1, 1])
            cursor.execute("""
                INSERT INTO post_votes (user_id, post_id, vote_type)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (voter_id, post_id, vote_type))

    # Comment Votes
    for comment_id in comment_ids:
        for _ in range(random.randint(1, 4)):
            voter_id = random.choice(users)
            vote_type = random.choice([-1, 1])
            cursor.execute("""
                INSERT INTO comment_votes (user_id, comment_id, vote_type)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (voter_id, comment_id, vote_type))

    print(f"Inserted {len(post_ids)} forum posts, {len(comment_ids)} comments.")

if __name__ == "__main__":
    main()
