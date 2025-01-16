from fastapi import APIRouter
from loguru import logger
from app.utils.twitter import handle_twitter_request, twitter_client
from app.utils.twitter.decorators import handle_twitter_endpoint
from app.models.schemas.search import TimelineParams, TweetData

router = APIRouter()

@router.post(
    "/tweets/for-you",
    tags=["tweets"],
    summary="Get tweets for you",
    description="Retrieve tweets for the user's For You timeline"
)
@handle_twitter_endpoint("get tweets for you")
async def get_latest_user_timeline(params: TimelineParams):
    logger.info("🔎  Fetching user timeline (For You)...")

    async def get_timeline_tweets():
        return await twitter_client.client.get_timeline()

    tweets = await handle_twitter_request(get_timeline_tweets)
    results = []

    for i, tweet in enumerate(tweets[:params.minimum_tweets]):
        tweet_data = twitter_client.process_tweet(tweet, i + 1)
        results.append(TweetData(**tweet_data))

    return results
