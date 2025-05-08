#!/usr/bin/env python3

import psycopg
from faker import Faker
import random
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
                cursor.execute('TRUNCATE TABLE issue_issue_types RESTART IDENTITY CASCADE')
                cursor.execute('TRUNCATE TABLE issue_issue_subtypes RESTART IDENTITY CASCADE')

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
                    agency_id = random.choice(agencies)
                    council_id = random.choice(councils)
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
                        INSERT INTO issues (user_id, latitude, longitude, location, address, description, severity, status, datetime_reported, datetime_acknowledged, datetime_closed, datetime_updated, agency_id, town_council_id, planning_area_id, subzone_id, is_public)
                        VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING issue_id
                    """, (
                        user_id, latitude, longitude, longitude, latitude, address,
                        f"Issue reported at {address}", severity, status,
                        datetime_reported, datetime_acknowledged, datetime_closed, datetime_updated,
                        agency_id, council_id, planning_area_id, subzone_id, is_public
                    ))
                    issue_id = cursor.fetchone()[0]
                    inserted_issue_ids.append(issue_id)

                    # Insert random type-subtype mappings
                    selected_types = random.sample(issue_types, k=random.randint(1, min(2, len(issue_types))))
                    for type_id in selected_types:
                        cursor.execute('INSERT INTO issue_issue_types (issue_id, issue_type_id) VALUES (%s, %s)', (issue_id, type_id))
                        subtype_ids = type_to_subtypes.get(type_id)
                        if subtype_ids:
                            selected_subtypes = random.sample(subtype_ids, k=random.randint(1, min(2, len(subtype_ids))))
                            for subtype_id in selected_subtypes:
                                cursor.execute('INSERT INTO issue_issue_subtypes (issue_id, issue_subtype_id) VALUES (%s, %s)', (issue_id, subtype_id))

                print(f"Inserted {len(inserted_issue_ids)} issues successfully.")
            except Exception as e:
                print(f"Error seeding issues: {e}")
                raise

    print("Seeding issues done.")

if __name__ == "__main__":
    main()
