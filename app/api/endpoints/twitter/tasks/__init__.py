from fastapi import APIRouter
from app.api.endpoints.twitter.tasks.handle_mention import router as handle_mention_router
from app.api.endpoints.twitter.tasks.ask_model import router as ask_model_router

router = APIRouter()

router.include_router(handle_mention_router, tags=["tasks"])
router.include_router(ask_model_router, tags=["tasks"])