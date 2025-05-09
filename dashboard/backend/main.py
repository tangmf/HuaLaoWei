"""
main.py

FastAPI application entrypoint for the Municipal Dashboard backend.

Author: Fleming Siow
Date: 5th May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

from fastapi import FastAPI
from dashboard.backend.db.database import lifespan
from dashboard.backend.api.v1.endpoints import issues, meta, subzone, forecast

# --------------------------------------------------------
# Application Factory
# --------------------------------------------------------

app = FastAPI(
    title="Municipal Dashboard API",
    version="1.0.0",
    lifespan=lifespan
)

# --------------------------------------------------------
# Routers Registration
# --------------------------------------------------------

app.include_router(issues.router)
app.include_router(meta.router)
app.include_router(subzone.router)
app.include_router(forecast.router)

# --------------------------------------------------------
# Health Check Endpoint
# --------------------------------------------------------

@app.get("/", tags=["Health Check"])
async def health_check():
    return {"status": "OK"}
