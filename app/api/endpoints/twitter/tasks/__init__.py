from fastapi import APIRouter
from app.api.endpoints.twitter.tasks.reply_tweet import router as reply_tweet_router
from app.api.endpoints.twitter.tasks.ask_model import router as ask_model_router

router = APIRouter()

router.include_router(reply_tweet_router, tags=["tasks"])
router.include_router(ask_model_router, tags=["tasks"])