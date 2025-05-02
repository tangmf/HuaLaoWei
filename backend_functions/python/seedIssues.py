# Python
import psycopg2
import csv
from datetime import datetime

def safe_timestamp(value):
    try:
        value = value.strip()
        if not value:
            return None
        for fmt in ("%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise ValueError(f"Unrecognized timestamp format: {value}")
    except Exception as e:
        raise ValueError(f"Invalid timestamp '{value}': {e}")

connection = psycopg2.connect(
    user='postgres',
    password='fyukiAmane03!',
    host='localhost',
    port='5432',
    database='municipal_app'
)

csv_file_path = 'issues.csv'
inserted = 0
skipped = 0

# Python
try:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM issues;")
            print("Cleared existing records from issues table.")

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader, start=1):
            try:
                row['latitude'] = float(row['latitude'])
                row['longitude'] = float(row['longitude'])
                row['user_id'] = int(row['user_id']) if row['user_id'] else None
                row['issue_type_id'] = int(row['issue_type_id']) if row['issue_type_id'] else None
                row['issue_subcategory_id'] = int(row['issue_subcategory_id']) if row['issue_subcategory_id'] else None
                row['agency_id'] = int(row['agency_id']) if row['agency_id'] else None
                row['town_council_id'] = int(row['town_council_id']) if row['town_council_id'] else None
                row['is_public'] = row['is_public'].strip().lower() == 'true'
                row['datetime_reported'] = safe_timestamp(row.get('datetime_reported', ''))
                row['datetime_acknowledged'] = safe_timestamp(row.get('datetime_acknowledged', ''))
                row['datetime_closed'] = safe_timestamp(row.get('datetime_closed', ''))
                row['datetime_updated'] = safe_timestamp(row.get('datetime_updated', ''))
                row['subzone_id'] = int(row['subzone_id']) if row['subzone_id'] else None
                row['planning_area_id'] = int(row['planning_area_id']) if row['planning_area_id'] else None

                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO issues (
                            user_id, issue_type_id, issue_subcategory_id,
                            latitude, longitude, full_address, location,
                            description, severity, status,
                            datetime_reported, datetime_acknowledged,
                            datetime_closed, datetime_updated,
                            agency_id, town_council_id, is_public, subzone_id, planning_area_id
                        ) VALUES (
                            %(user_id)s, %(issue_type_id)s, %(issue_subcategory_id)s,
                            %(latitude)s, %(longitude)s, %(full_address)s,
                            ST_SetSRID(ST_MakePoint(%(longitude)s, %(latitude)s), 4326),
                            %(description)s, %(severity)s, %(status)s,
                            %(datetime_reported)s, %(datetime_acknowledged)s,
                            %(datetime_closed)s, %(datetime_updated)s,
                            %(agency_id)s, %(town_council_id)s, %(is_public)s, %(subzone_id)s, %(planning_area_id)s
                        )
                    """, row)
                    connection.commit()
                    inserted += 1
            except Exception as row_err:
                connection.rollback()
                skipped += 1
                print(f"Row {idx} skipped: {row_err}\nData: {row}")

    print(f"Insert completed. {inserted} rows inserted, {skipped} rows skipped.")
except Exception as e:
    print("Error:", e)
finally:
    connection.close()