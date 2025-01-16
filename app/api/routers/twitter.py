from fastapi import APIRouter
from app.api.endpoints.twitter.tweets import router as tweets_router
from app.api.endpoints.twitter.tasks import router as tasks_router

router = APIRouter()

router.include_router(tweets_router, prefix="/twitter", tags=["tweets"])
router.include_router(tasks_router, prefix="/twitter", tags=["tasks"])
