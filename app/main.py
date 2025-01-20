import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader, APIKeyQuery
from loguru import logger

from app.api.routers import router as api_router

load_dotenv()

API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("API_KEY")

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)

async def get_api_key(
    api_key_header: str = Security(api_key_header),
    api_key_query: str = Security(api_key_query),
) -> str:
    if api_key_header == API_KEY:
        return api_key_header
    if api_key_query == API_KEY:
        return api_key_query
    raise HTTPException(status_code=401, detail="Invalid API Key")

app = FastAPI(
    title="My API",
    description="My awesome API",
    version="0.1.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    security=[{"api_key": []}],
)
app.include_router(api_router, dependencies=[Depends(get_api_key)])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application...")
