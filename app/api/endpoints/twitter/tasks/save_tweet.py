from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from supabase import Client

from app.models.schemas.tweet import TweetDetails, TwitterTweet
from app.services.system.supabase import get_supabase
from app.services.twitter.tweet_service import save_twitter_tweet
from app.utils.twitter import process_tweet_details, normalize_tweet_data
from app.utils.twitter.decorators import handle_twitter_endpoint

from ..tweets.single_tweet import get_tweet_by_id

router = APIRouter()

supabase_dependency = Depends(get_supabase)

@router.post(
    "/tasks/save-tweets/{tweet_id}",
    tags=["tasks"],
    response_model=TweetDetails,
    summary="Save tweet to database",
    description="Saves tweet to database"
)
@handle_twitter_endpoint("save tweet")
async def save_tweet(
    tweet_id: str,
    supabase: Client = supabase_dependency
):
    tweet_details = await get_tweet_by_id(tweet_id)

    if not tweet_details:
        raise HTTPException(status_code=404, detail="Tweet not found")

    logger.info(f"✅  Successfully fetched tweet {tweet_details.id}")

    processed_tweet = process_tweet_details(tweet_details)

    twitter_tweet = TwitterTweet(**normalize_tweet_data(processed_tweet.model_dump()))

    logger.info(f"💾  Saving tweet {tweet_id} to database...")
    await save_twitter_tweet(supabase, twitter_tweet.model_dump())
    logger.info(f"✅  Successfully saved tweet {tweet_id} to database")


    return processed_tweet
