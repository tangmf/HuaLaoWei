# app.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from loaders.model_loader import preload_all_models
from routers import forecast_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    preload_all_models()
    yield

app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(forecast_router.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)