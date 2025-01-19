import json

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

from app.api.endpoints.ai.gen_text import gen_text
from app.models.schemas.tasks import HandleMentionRequest
from app.models.schemas.tweet import CreateTweetRequest, TweetDetails
from app.utils.twitter.decorators import handle_twitter_endpoint

from ..tweets.like import like_tweet
from ..tweets.new import create_tweet
from ..tweets.replies import get_tweet_replies
from ..tweets.single_tweet import get_tweet_by_id

router = APIRouter()

class ContextTweet(BaseModel):
    id: str
    text: str
    lang: str
    author_name: str

@router.post(
    "/tasks/reply-mention",
    tags=["tasks"],
    response_model=TweetDetails,
    summary="Process a Twitter mention and generate a reply",
    description="This endpoint processes a Twitter mention, fetches the context, and uses an LLM to generate a relevant reply."
)
@handle_twitter_endpoint("reply mention")
async def reply_mention(request: HandleMentionRequest):
    tweet_id = request.tweet_id
    tweet_with_mention = await get_tweet_by_id(tweet_id)
    logger.info(f"✅  Successfully fetched mentioned tweet {tweet_with_mention.id}")

    # Initialize context with the current tweet
    context = [{
        "id": tweet_with_mention.id,
        "text": tweet_with_mention.display_text,
        "lang": tweet_with_mention.lang,
        "author_name": tweet_with_mention.author.name
    }]

    # If the tweet is a reply, fetch the conversation context
    if tweet_with_mention.in_reply_to:
        branch = await get_tweet_replies(tweet_with_mention.in_reply_to, limit=request.limit or 100)
        main_tweet = branch.main_tweet
        logger.info(f"✅  Successfully fetched base tweet {main_tweet.id}")

        # Add main tweet at the beginning
        context.insert(0, {
            "id": main_tweet.id,
            "text": main_tweet.display_text,
            "lang": main_tweet.lang,
            "author_name": main_tweet.author.name
        })

        # Add replies in between
        for reply in branch.replies:
            if reply.id != tweet_with_mention.id:  # Avoid duplicating the mention tweet
                context.insert(-1, {
                    "id": reply.id,
                    "text": reply.display_text,
                    "lang": reply.lang,
                    "author_name": reply.author.name
                })

    # TODO: Improve the prompt for handle different cases
    llm_request = f"""You are given an array of tweets:
{json.dumps(context)}

Here the first tweet is the base tweet and the last tweet is the user's current tweet.
All other tweets are just for context and don't require a response.

You need to decide which of these two tweets is worth replying to:
- If the last tweet is meaningful and long, then you can reply to it.
- If the last tweet is an invitation to reply to the first tweet, then reply to the first.

Your response should be a JSON object only with the following fields:
- "target_tweet_id": The ID of the tweet to reply to.
- "reply_text": The text of the reply.

The required response format is:
{json.dumps({"target_tweet_id": "1234567890", "reply_text": "Hello, how are you?"})}

The reply_text should be a direct response to the chosen tweet that:
1. Builds upon or challenges the specific point made in the original tweet
2. Brings new, non-obvious technical insights relevant to the tweet's context
3. Shows deep expertise while maintaining conversational tone
4. Must be between 100 and 280 characters

The answer must contain only the object and nothing else, this is critically important.
"""

    response = await gen_text(llm_request)

    try:
        structured_response = json.loads(response)
    except (json.JSONDecodeError, TypeError) as err:
        logger.error("Failed to parse model response as JSON")
        raise HTTPException(status_code=500, detail="Model returned invalid JSON") from err

    if not structured_response:
        raise HTTPException(status_code=500, detail="Model returned empty response")

    if structured_response.get("target_tweet_id") != tweet_id:
        await like_tweet(tweet_id)
        logger.info(f"💛 Liking mention target tweet {tweet_id}")
    elif tweet_with_mention.in_reply_to:
        await like_tweet(branch.main_tweet.id)
        logger.info(f"💛 Liking main tweet {branch.main_tweet.id}")

    tweet_request = CreateTweetRequest(
        text=structured_response.get("reply_text"),
        reply_to=structured_response.get("target_tweet_id")
    )

    # TODO: If replied the main tweet before, then reply tweet_with_mention (if have since and it's a positive tweet)
    reply = await create_tweet(tweet_request)

    if not reply:
        raise HTTPException(status_code=500, detail="Failed to create reply tweet")

    return reply
