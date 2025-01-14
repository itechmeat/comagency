from fastapi import APIRouter
from loguru import logger
from app.utils.twitter import handle_twitter_request, twitter_client
from app.utils.twitter.decorators import handle_twitter_endpoint

router = APIRouter()

@router.post(
    "/tweets/{tweet_id}/unlike",
    tags=["tweets"],
    summary="Unfavorite a tweet",
    description="Unfavorite a tweet by its ID"
)
@handle_twitter_endpoint("unfavorite tweet")
async def unlike_tweet(tweet_id: int):
    logger.info(f"🎯  Attempting to unfavorite tweet {tweet_id}")

    async def do_favorite():
        return await twitter_client.client.unfavorite_tweet(tweet_id)

    await handle_twitter_request(do_favorite)
    logger.info(f"💜  Successfully unfavorited tweet {tweet_id}")
    return {"status": "success", "tweet_id": tweet_id}
