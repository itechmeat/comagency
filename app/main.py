from fastapi import FastAPI
from app.api.routers import router as api_router
from loguru import logger

app = FastAPI()
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application...")
