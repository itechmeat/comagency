from fastapi import FastAPI
from app.api.routers.system import router as health_router
from app.api.routers.twitter import router as twitter_router
from loguru import logger

app = FastAPI()
app.include_router(health_router)
app.include_router(twitter_router)
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application...")
