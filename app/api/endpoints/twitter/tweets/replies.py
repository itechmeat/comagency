from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.schemas.tweet import TweetThread
from loguru import logger
from app.utils.twitter import handle_twitter_request, process_tweet_details, twitter_client
from app.utils.twitter.decorators import handle_twitter_endpoint

router = APIRouter()

@router.get(
    "/tweets/{tweet_id}/replies",
    response_model=TweetThread,
    tags=["tweets"],
    summary="Get tweet replies",
    description=(
        "Retrieve replies for a specific tweet with pagination support. "
        "Returns the main tweet and its replies up to the specified limit."
    )
)
@handle_twitter_endpoint("get tweet replies")
async def get_tweet_replies(
    tweet_id: str,
    limit: int = Query(default=100, le=1000, description="Maximum number of replies to fetch"),
    until_id: Optional[str] = Query(None, description="Collect replies until this tweet ID (inclusive)")
):
    """Get replies for a specific tweet with pagination"""
    logger.info(f"🔎  Fetching up to {limit} replies for tweet {tweet_id} (until_id={until_id})...")

    async def fetch_replies():
        # Get main tweet first
        main_tweet = await twitter_client.client.get_tweet_by_id(tweet_id)
        if not main_tweet:
            raise HTTPException(status_code=404, detail="Tweet not found")

        main_tweet_details = process_tweet_details(main_tweet)

        # If tweet has no replies, return early
        if not main_tweet.replies:
            return TweetThread(main_tweet=main_tweet_details, replies=[])

        replies = []
        max_pages = 5  # Limit the number of pages
        page_count = 0

        # Get initial replies
        current_replies = main_tweet.replies
        while current_replies and len(replies) < limit and page_count < max_pages:
            # Process current page of replies
            for reply in current_replies[:limit - len(replies)]:
                reply_details = process_tweet_details(reply)
                replies.append(reply_details)

                # Check if we reached the until_id
                if until_id and reply_details.id == until_id:
                    return TweetThread(main_tweet=main_tweet_details, replies=replies)

            # Try to get next page
            has_next = await current_replies.next() if current_replies else None
            if len(replies) < limit and has_next:
                page_count += 1
                current_replies = await current_replies.next()
            else:
                break

        return TweetThread(
            main_tweet=main_tweet_details,
            replies=replies[:limit]  # Cut to requested limit
        )

    result = await handle_twitter_request(fetch_replies)
    logger.info(f"✅  Successfully fetched main tweet and {len(result.replies)} replies")
    return result