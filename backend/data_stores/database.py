from psycopg_pool import AsyncConnectionPool
from config.config import config

DB_CONFIG = config.data_stores["relational_db"]

dsn = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Create the AsyncConnectionPool immediately
db_client = AsyncConnectionPool(conninfo=dsn)
