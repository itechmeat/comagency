from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import BaseModel
from supabase import Client

from app.models.schemas.search import SearchParams
from app.services.system.supabase import get_supabase
from app.services.twitter.tweet_service import save_twitter_tweets_batch

from ..tweets.search import search_tweets

router = APIRouter()

supabase_dependency = Depends(get_supabase)

class HandleSearchRequest(BaseModel):
    phrases: List[str]

@router.post(
    "/tasks/save-search",
    tags=["tasks"],
    response_model=int,
    summary="Save search results for given phrases",
    description="Searches Twitter for given phrases and saves matching tweets"
)
async def save_search(request: HandleSearchRequest, supabase: Client = supabase_dependency):
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
        # Log the structure of the first tweet for debugging
        if tweets:
            logger.debug(f"Tweet structure: {dir(tweets[0])}")
            logger.debug(f"Tweet data: {tweets[0].dict()}")
        search_batch.append({"phrase": phrase, "tweets": tweets})

    results = []
    seen_ids = set()
    logger.info(f"✅  seen_ids: {len(seen_ids)}")

    for batch in search_batch:
        for tweet in batch['tweets']:
            tweet_data = tweet.dict()
            # Convert TweetData object to dictionary format that matches TwitterTweet model
            tweet_dict = {
                'id': tweet_data['tweet_id'],
                'text': tweet_data['text'],
                'display_text': tweet_data['text'],  # Required field
                'retweet_count': tweet_data['retweets'],
                'favorite_count': tweet_data['likes'],
                'author': {
                    'id': tweet_data['tweet_user_nick'],
                    'name': tweet_data['tweet_user_name'],
                    'username': tweet_data['tweet_user_nick'],
                    'profile_image_url': None
                },
                'lang': tweet_data['tweet_lang'],
                'photo_urls': tweet_data.get('photo_urls', []),
                'media': [],
                'in_reply_to_status_id': None,
                'in_reply_to_user_id': None,
                'in_reply_to_screen_name': None,
                'in_reply_to': None
            }

            if tweet_dict['id'] and tweet_dict['id'] not in seen_ids:
                seen_ids.add(tweet_dict['id'])
                results.append(tweet_dict)

    # Log the first result for debugging
    if results:
        logger.debug(f"First normalized tweet: {results[0]}")

    # Save the unique tweets to the database
    if results:
        saved_tweets = await save_twitter_tweets_batch(supabase, results)
        return len(saved_tweets)

    return 0