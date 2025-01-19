from fastapi import APIRouter, HTTPException
from loguru import logger

from app.models.schemas.tweet import TweetDetails
from app.utils.twitter import handle_twitter_request, process_tweet_details, twitter_client
from app.utils.twitter.decorators import handle_twitter_endpoint

router = APIRouter()

@router.get(
    "/tweets/{tweet_id}", 
    response_model=TweetDetails,
    tags=["tweets"],
    summary="Get a tweet by its ID",
    description="Retrieve details for a specific tweet by its ID"
)
@handle_twitter_endpoint("get tweet by id")
async def get_tweet_by_id(tweet_id: str):
    """Get a tweet by its ID"""
    logger.info(f"🔎  Fetching tweet with ID {tweet_id}...")

    async def fetch_tweet():
        tweet = await twitter_client.client.get_tweet_by_id(tweet_id)
        if not tweet:
            raise HTTPException(status_code=404, detail="Tweet not found")
        return tweet

    tweet_details = await handle_twitter_request(fetch_tweet)
    processed_tweet = process_tweet_details(tweet_details)
    logger.info(f"✅  Successfully fetched tweet {tweet_details.id}")

    return processed_tweet