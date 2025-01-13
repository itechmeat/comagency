from fastapi import APIRouter
from loguru import logger
from app.utils.twitter import handle_twitter_request, twitter_client
from app.utils.twitter.decorators import handle_twitter_endpoint
from app.models.schemas.search import TimelineParams, TweetData

router = APIRouter()

@router.post(
    "/tweets/latest",
    tags=["tweets"],
    summary="Get latest tweets from following timeline",
    description="Retrieve the latest tweets from the user's following timeline"
)
@handle_twitter_endpoint("get following timeline")
async def get_latest_user_timeline(params: TimelineParams):
    logger.info("🔎  Fetching latest timeline (Following)...")

    async def get_latest_timeline_tweets():
        return await twitter_client.client.get_latest_timeline()

    tweets = await handle_twitter_request(get_latest_timeline_tweets)
    results = []

    for i, tweet in enumerate(tweets[:params.minimum_tweets]):
        tweet_data = twitter_client.process_tweet(tweet, i + 1)
        results.append(TweetData(**tweet_data))

    return results
