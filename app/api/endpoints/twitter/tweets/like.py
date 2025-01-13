from fastapi import APIRouter
from app.models.schemas.tweet import TweetDetails
from loguru import logger
from app.utils.twitter import handle_twitter_request, twitter_client
from app.utils.twitter.decorators import handle_twitter_endpoint

router = APIRouter()

@router.post(
    "/tweets/{tweet_id}/like",
    tags=["tweets"],
    summary="Favorite a tweet",
    description="Favorite a tweet by its ID"
)
@handle_twitter_endpoint("favorite tweet")
async def favorite_tweet(tweet_id: int):
    logger.info(f"🎯  Attempting to favorite tweet {tweet_id}")

    async def do_favorite():
        return await twitter_client.client.favorite_tweet(tweet_id)

    result = await handle_twitter_request(do_favorite)
    logger.info(f"💜  Successfully favorited tweet {tweet_id}")
    return {"status": "success", "tweet_id": tweet_id}
