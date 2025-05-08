from psycopg_pool import AsyncConnectionPool
from contextlib import asynccontextmanager
from config.config import config

DB_CONF = config.data_stores["relational_db"]

dsn = f"postgresql://{DB_CONF['user']}:{DB_CONF['password']}@{DB_CONF['host']}:{DB_CONF['port']}/{DB_CONF['database']}"
pool = AsyncConnectionPool(conninfo=dsn)

@asynccontextmanager
async def lifespan(app):
    app.state.pool = pool
    yield
    await pool.close()
