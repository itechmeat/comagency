from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas.tweet import TweetDetails, TwitterTweet
from loguru import logger
from app.utils.twitter import handle_twitter_request, process_tweet_details, twitter_client
from app.utils.twitter.decorators import handle_twitter_endpoint
from supabase import Client
from app.services.system.supabase import get_supabase
from app.services.twitter.tweet_service import save_twitter_tweet

router = APIRouter()

supabase_dependency = Depends(get_supabase)

@router.get(
    "/tweets/{tweet_id}", 
    response_model=TweetDetails,
    tags=["tweets"],
    summary="Get a tweet by its ID",
    description="Retrieve details for a specific tweet by its ID"
)
@handle_twitter_endpoint("get tweet by id")
async def get_tweet_by_id(
    tweet_id: str,
    supabase: Client = supabase_dependency
):
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

    twitter_tweet = TwitterTweet(
        id=processed_tweet.id,
        text=processed_tweet.text,
        display_text=processed_tweet.display_text,
        lang=processed_tweet.lang,
        retweet_count=processed_tweet.retweet_count,
        favorite_count=processed_tweet.favorite_count,
        author={
            "id": processed_tweet.author.id,
            "name": processed_tweet.author.name,
            "username": processed_tweet.author.username,
            "profile_image_url": processed_tweet.author.profile_image_url
        },
        in_reply_to_status_id=processed_tweet.in_reply_to_status_id,
        in_reply_to_user_id=processed_tweet.in_reply_to_user_id,
        in_reply_to_screen_name=processed_tweet.in_reply_to_screen_name,
        in_reply_to=processed_tweet.in_reply_to,
        photo_urls=processed_tweet.photo_urls
    )

    try:
        logger.info(f"💾  Saving tweet {tweet_id} to database...")
        await save_twitter_tweet(supabase, twitter_tweet.model_dump())
        logger.info(f"✅  Successfully saved tweet {tweet_id} to database")
    except Exception as e:
        logger.error(f"❌  Error saving tweet to database: {str(e)}")

    return processed_tweet