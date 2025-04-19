import os
import time
import subprocess
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("ENV", "dev")
ENV = os.getenv("ENV")

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")

print("Waiting for PostgreSQL to be available...")

for i in range(30):
    try:
        result = subprocess.run(
            ["nc", "-z", DB_HOST, DB_PORT],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            print("PostgreSQL is reachable")
            break
        else:
            print(f"[{i+1}/30] PostgreSQL not ready")
    except FileNotFoundError as e:
        print(f"[{i+1}/30] Error: 'nc' not found. Make sure netcat is installed in the Docker image.")
        exit(1)
    time.sleep(2)
else:
    print("PostgreSQL did not become ready in time. Exiting.")
    exit(1)

if ENV == "dev":
    print("Running setup scripts...")

    subprocess.run(["python", "scripts/postgresql_setup/01_setup_db.py"], check=True)
    subprocess.run(["python", "scripts/postgresql_setup/02_generate_issues.py"], check=True)
    subprocess.run(["python", "scripts/save_cache.py"], check=True)
    subprocess.run(["python", "scripts/seed_vector_store.py"], check=True)
    with open("/tmp/setup_done", "w") as f:
        f.write("1")

print("Starting FastAPI server at http://localhost:8000")
subprocess.run(["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])
