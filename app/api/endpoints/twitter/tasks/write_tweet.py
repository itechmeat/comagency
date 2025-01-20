from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from supabase import Client

from app.models.schemas.tweet import CreateTweetRequest, TweetDetails, TwitterTweet
from app.services.system.supabase import get_supabase
from app.services.twitter.tweet_service import save_twitter_post
from app.utils.twitter import process_tweet_details, normalize_tweet_data
from app.utils.twitter.decorators import handle_twitter_endpoint

from ..tweets.new import create_tweet

router = APIRouter()

supabase_dependency = Depends(get_supabase)

@router.post(
    "/tasks/write-tweet",
    tags=["tasks"],
    response_model=TweetDetails,
    summary="Post tweet and save to database",
    description=""
)
@handle_twitter_endpoint("write tweet")
async def write_tweet(
    request: CreateTweetRequest,
    supabase: Client = supabase_dependency
):
    tweet_details = await create_tweet(request)

    if not tweet_details:
        raise HTTPException(status_code=404, detail="Post not created")

    logger.info(f"✅  Successfully fetched post {tweet_details.id}")

    processed_tweet = process_tweet_details(tweet_details)

    twitter_tweet = TwitterTweet(**normalize_tweet_data(processed_tweet.model_dump()))

    logger.info(f"💾  Saving tweet {twitter_tweet.id} to database...")
    await save_twitter_post(supabase, twitter_tweet.model_dump())
    logger.info(f"✅  Successfully saved tweet {twitter_tweet.id} to database")


    return processed_tweet
