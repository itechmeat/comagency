from fastapi import APIRouter
from app.api.endpoints.system.health import router as health_router

router = APIRouter()

router.include_router(health_router, prefix="/health", tags=["health"])
