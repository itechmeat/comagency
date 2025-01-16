import json
from typing import List
from datetime import date, timedelta

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

from app.models.schemas.tweet import TweetDetails, CreateTweetRequest
from ..tweets.search import search_tweets
from ..tweets.like import like_tweet
from ..tweets.new import create_tweet
from .ask_model import ask_model
from app.models.schemas.search import SearchParams

router = APIRouter()

class ContextTweet(BaseModel):
    id: str
    text: str
    lang: str
    author_name: str

class HandleSearchRequest(BaseModel):
    phrases: List[str]

class SearchResultTweet(BaseModel):
    tweet_id: str
    tweet_user_nick: str
    text: str
    retweets: int
    likes: int

@router.post(
    "/tasks/reply-search",
    tags=["tasks"],
    response_model=TweetDetails,
    summary="Search for tweets matching given phrases",
    description="Searches for tweets containing exact phrases with minimum engagement requirements"
)
async def reply_search(request: HandleSearchRequest):
    search_batch = []
    yesterday = date.today() - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")

    for phrase in request.phrases:
        params = SearchParams(
            query=f'"{phrase}" min_replies:1 min_faves:30 min_retweets:1 lang:en since:{yesterday_str} -filter:replies',
            minimum_tweets=10
        )
        search_result = await search_tweets(params)
        tweets = getattr(search_result, 'tweets', [])
        search_batch.append({"phrase": phrase, "tweets": tweets})

    results = []
    seen_ids = set()

    for batch in search_batch:
        for tweet_data in batch["tweets"]:
            try:
                tweet_id = tweet_data.tweet_id

                if tweet_id not in seen_ids:
                    seen_ids.add(tweet_id)
                    photo_urls = tweet_data.photo_urls

                    if not photo_urls:
                        results.append(SearchResultTweet(
                            tweet_id=str(tweet_id),
                            tweet_user_nick=tweet_data.tweet_user_nick,
                            text=tweet_data.text,
                            retweets=tweet_data.retweets,
                            likes=tweet_data.likes
                        ))

            except Exception as e:
                logger.error(f"Error processing tweet: {e}")
                continue

    logger.info(f"🔎  Found {len(results)} unique tweets matching search criteria")

    # TODO: Improve the prompt for handle different cases
    llm_request = f"""# AI Tweet Rating System

You are given an array of tweets:
{json.dumps([tweet.model_dump() for tweet in results])}

Your Task:
Analyze tweets to find the one with the highest rating based on this formula, then return BOTH its ID and an appropriate reply to that tweet:
Final Score = (AI_Relevance × 5) + (Retweets × 2) + (Likes × 0.5) + (Number_of_Mentions × -10) + (Negative_Factors × -50)

Where:
1. AI Relevance (0-100):
    - Technical AI discussion: high score
    - AI development insights: high score
    - Educational AI content: high score
    - Marketing/promotional AI content: lower score

2. Retweets: multiply by 2
3. Likes: multiply by 0.5
4. Mentions: count '@' symbols and multiply by -10

5. Negative Factors (count each occurrence, multiply total by -50):
IMPORTANT: The presence of ANY of these factors should SEVERELY reduce the tweet's score!

Major Negative Factors (each counts as 2 occurrences):
- Price discussion or market speculation of any kind
- Token/coin listings with $ symbol (e.g. "$BTC", "$AI")
- Market cap mentions
- Terms: "bull run", "moon", "pump", "ATH", "gains"
- Price predictions or "x times" mentions
- Lists of tokens/coins to buy
- Investment advice or trading suggestions

Minor Negative Factors (each counts as 1 occurrence):
- Giveaways or airdrops
- Multiple token/coin mentions
- References to trading or markets
- Use of rocket emojis 🚀 or similar hype indicators
- Mentions of "gem", "early", or similar promotional terms

NOTE: If a tweet contains 3 or more negative factors, it should be eliminated from consideration completely!

CRITICAL:
- Response must be ONLY an object with the tweet ID string and reply text for this tweet.
- No code, no explanations, no formatting
- No quotes, no JSON, no extra characters
- Just the ID number and nothing else

Response Rules:
❌ DO NOT include:
- Code blocks
- Explanations
- Quotes
- JSON formatting
- Extra text
- Calculations
- Multiple IDs
- Anything else

✅ ONLY include:
- An object with two fields:
1. target_tweet_id: the ID of the highest scoring tweet
2. reply_text: your response/reply to this tweet. The reply should engage with the tweet's content and continue the discussion about AI in a meaningful way.

Remember: The response should be IDENTICAL in format to this example:
{json.dumps({"target_tweet_id": "1234567890", "reply_text": "Interesting point about AI agents! The integration of complex models is indeed challenging, but it's crucial for achieving meaningful AI capabilities. What specific technical challenges have you encountered in your development process?"})}

Response Format Requirements:

The reply_text should be a direct response to the chosen tweet that:
1. Builds upon or challenges the specific point made in the original tweet
2. Brings new, non-obvious technical insights relevant to the tweet's context
3. Shows deep expertise while maintaining conversational tone
4. Must be between 100 and 280 characters

Example good responses:
- To a tweet about AI agent memory: "True, but current vector stores still struggle with temporal consistency. Recent research shows episodic memory models perform 40% better for long-term context retention."
- To a tweet about AI autonomous trading: "Interesting point. Latest transformer architectures actually show 3x better market prediction when combining on-chain data with technical analysis, contrary to traditional models."

DO NOT:
- State generic facts about AI
- Give textbook-style explanations
- Make obvious statements
- Ignore the specific context of the tweet

DO:
- Directly engage with the tweet's main point
- Add surprising or cutting-edge information
- Challenge assumptions with data
- Share specific, recent findings
- Keep expertise conversational
Both fields should be strings.
"""

    answer = await ask_model(llm_request)
    logger.info(f"🤖  Model answer: {answer}")


    try:
        structured_response = json.loads(answer)
    except (json.JSONDecodeError, TypeError) as err:
        logger.error("Failed to parse model response as JSON")
        raise HTTPException(status_code=500, detail="Model returned invalid JSON") from err

    if not structured_response:
        raise HTTPException(status_code=500, detail="Model returned empty response")

    await like_tweet(structured_response.get("target_tweet_id"))
    logger.info(f"💛 Liking mention target tweet {structured_response.get('target_tweet_id')}")

    tweet_request = CreateTweetRequest(
        text=structured_response.get("reply_text"),
        reply_to=structured_response.get("target_tweet_id")
    )

    # TODO: If replied the main tweet before, then reply tweet_with_mention (if have since and it's a positive tweet)
    reply = await create_tweet(tweet_request)

    if not reply:
        raise HTTPException(status_code=500, detail="Failed to create reply tweet")

    return reply
