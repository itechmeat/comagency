from fastapi import APIRouter
from app.api.endpoints.twitter.tweets import router as tweets_router

router = APIRouter()

router.include_router(tweets_router, prefix="/twitter", tags=["tweets"])