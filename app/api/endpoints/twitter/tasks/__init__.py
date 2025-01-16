from fastapi import APIRouter
from app.api.endpoints.twitter.tasks.reply_mention import router as reply_mention_router
from app.api.endpoints.twitter.tasks.reply_comment import router as reply_comment_router
from app.api.endpoints.twitter.tasks.reply_search import router as reply_search_router
from app.api.endpoints.twitter.tasks.ask_model import router as ask_model_router

router = APIRouter()

router.include_router(reply_mention_router, tags=["tasks"])
router.include_router(reply_comment_router, tags=["tasks"])
router.include_router(reply_search_router, tags=["tasks"])
router.include_router(ask_model_router, tags=["tasks"])