from fastapi import APIRouter, HTTPException
from loguru import logger
from app.models.schemas.tweet import TweetDetails
from app.utils.twitter.decorators import handle_twitter_endpoint
from ..tweets.single_tweet import get_tweet_by_id
from ..tweets.like import like_tweet

router = APIRouter()

@router.post(
    "/tasks/handle-mention",
    tags=["tasks"],
    response_model=TweetDetails,
    summary="Handle mention",
    description="Handle mention"
)
@handle_twitter_endpoint("handle mention")
async def handle_mention(tweet_id: str):
    # Fetch the mentioned tweet using the existing endpoint
    tweet_with_mention = await get_tweet_by_id(tweet_id)
    logger.info(f"✅  Successfully fetched mentioned tweet {tweet_with_mention.id}")
    logger.info(tweet_with_mention.text)
    
    # If the tweet is a reply, fetch the original tweet
    if tweet_with_mention.in_reply_to:
        await like_tweet(tweet_id)
        base_tweet = await get_tweet_by_id(tweet_with_mention.in_reply_to)
        logger.info(f"✅  Successfully fetched base tweet {base_tweet.id}")
        logger.info(base_tweet.text)
        return base_tweet

    return base_tweet or tweet_with_mention