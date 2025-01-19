from fastapi import APIRouter
from app.models.schemas.search import SearchParams, SearchResponse, TimelineParams
from loguru import logger
import time
from app.utils.twitter import handle_twitter_request, twitter_client
from app.utils.twitter.decorators import handle_twitter_endpoint
from secrets import randbelow

router = APIRouter()

async def get_tweets(params: SearchParams | TimelineParams):
    logger.info('🔎  Fetching tweets from Twitter API...')
    if isinstance(params, SearchParams):
        return await twitter_client.client.search_tweet(params.query, product='Latest')
    elif isinstance(params, TimelineParams):
        # Split requests for timeline and latest_timeline
        if getattr(params, 'is_latest', False):
            return await twitter_client.client.get_latest_timeline()
        else:
            return await twitter_client.client.get_timeline()

@router.post(
    "/tweets/search",
    tags=["tweets"],
    response_model=SearchResponse,
    summary="Search for tweets",
    description="Search for tweets based on a query"
)
@handle_twitter_endpoint("search tweets")
async def search_tweets(params: SearchParams):
    tweet_count = 0
    tweets = None
    results = []

    async def get_tweets_func():
        nonlocal tweets
        if tweets is None:
            return await get_tweets(params)
        else:
            wait_time = randbelow(6) + 5  # Generates a random number between 5 and 10
            logger.info(f'⏳  Getting next tweets after {wait_time} seconds ...')
            time.sleep(wait_time)
            return await tweets.next()

    while tweet_count < params.minimum_tweets:
        tweets = await handle_twitter_request(get_tweets_func)
        if not tweets:
            break

        for tweet in tweets:
            tweet_count += 1
            tweet_data = twitter_client.process_tweet(tweet, tweet_count)
            results.append(tweet_data)

            if tweet_count >= params.minimum_tweets:
                break

    return SearchResponse(tweets=results)