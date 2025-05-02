import psycopg2

# Config: DB connection
conn = psycopg2.connect(
    user='postgres',
    password='fyukiAmane03!',
    host='localhost',
    port='5432',
    database='municipal_app'
)

def execute_sql_file(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()
        statements = sql.strip().split(';')
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                cursor.execute(stmt + ';')

try:
    with conn:
        with conn.cursor() as cur:
            print("📍 Inserting planning areas...")
            execute_sql_file(cur, "seed_planning_areas.sql")

            print("🗺️ Inserting subzones...")
            execute_sql_file(cur, "seed_subzones.sql")

            print("✅ Data inserted successfully.")
except Exception as e:
    print("❌ Error:", e)
    conn.rollback()
finally:
    conn.close()
