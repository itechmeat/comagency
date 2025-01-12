from fastapi import APIRouter, HTTPException, Query
from app.models.schemas.tweet import TweetDetails
from loguru import logger
from app.utils.twitter.api_utils import handle_twitter_request, twitter_client, ExecutionStopError
from app.utils.twitter.tweet_utils import process_tweet_details
router = APIRouter()

@router.get("/{tweet_id}", response_model=TweetDetails)
async def get_tweet_by_id(tweet_id: str):
    """Get a tweet by its ID"""
    logger.info(f"🔎  Fetching tweet with ID {tweet_id}...")
    
    async def fetch_tweet():
        tweet = await twitter_client.client.get_tweet_by_id(tweet_id)
        if not tweet:
            raise HTTPException(status_code=404, detail="Tweet not found")
        return tweet

    try:
        tweet_details = await handle_twitter_request(fetch_tweet)
        logger.info(f"✅  Successfully fetched tweet {tweet_details.id}")
        return process_tweet_details(tweet_details)
        
    except ExecutionStopError:
        raise
    except Exception as e:
        logger.error(f"Failed to get tweet {tweet_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))