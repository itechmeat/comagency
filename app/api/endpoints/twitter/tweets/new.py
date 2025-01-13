from fastapi import APIRouter, HTTPException
from app.models.schemas.tweet import TweetDetails, CreateTweetRequest
from loguru import logger
from app.utils.twitter import handle_twitter_request, process_tweet_details, twitter_client
from app.utils.twitter.decorators import handle_twitter_endpoint

router = APIRouter()

@router.post(
    "/tweets/new", 
    response_model=TweetDetails,
    tags=["tweets"],
    summary="Create a new tweet",
    description="Create a new tweet, optionally as a reply to another tweet"
)
@handle_twitter_endpoint("create tweet")
async def create_tweet(request: CreateTweetRequest):
    """Create a new tweet, optionally as a reply to another tweet"""
    logger.info(f"📝 Creating new tweet{' as reply' if request.reply_to else ''}")

    async def post_tweet():
        # If this is a reply, we need to include reply parameters
        if request.reply_to:
            # Get the original tweet to get its author info
            original_tweet = await twitter_client.client.get_tweet_by_id(request.reply_to)
            if not original_tweet:
                raise HTTPException(status_code=404, detail="Reply target tweet not found")

            return await twitter_client.client.create_tweet(
                text=request.text,
                reply_to=request.reply_to
            )
        else:
            # Regular tweet without reply
            return await twitter_client.client.create_tweet(text=request.text)

    tweet = await handle_twitter_request(post_tweet)
    tweet_details = process_tweet_details(tweet)
    logger.info(f"✅ Successfully posted tweet {tweet_details.id}")
    return tweet_details
