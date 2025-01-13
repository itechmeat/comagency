from fastapi import APIRouter
from app.api.endpoints.twitter.tweets.new import router as new_tweet_router
from app.api.endpoints.twitter.tweets.single_tweet import router as single_tweet_router
from app.api.endpoints.twitter.tweets.replies import router as replies_router
from app.api.endpoints.twitter.tweets.like import router as like_router
from app.api.endpoints.twitter.tweets.unlike import router as unlike_router
from app.api.endpoints.twitter.tweets.search import router as search_router
from app.api.endpoints.twitter.tweets.latest import router as latest_router
from app.api.endpoints.twitter.tweets.for_you import router as for_you_router

router = APIRouter()

router.include_router(new_tweet_router, tags=["tweets"])
router.include_router(single_tweet_router, tags=["tweets"])
router.include_router(replies_router, tags=["tweets"])
router.include_router(like_router, tags=["tweets"])
router.include_router(unlike_router, tags=["tweets"])
router.include_router(search_router, tags=["tweets"])
router.include_router(latest_router, tags=["tweets"])
router.include_router(for_you_router, tags=["tweets"])