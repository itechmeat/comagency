from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import BaseModel
from supabase import Client

from app.models.schemas.search import SearchParams
from app.services.system.supabase import get_supabase
from app.services.twitter.tweet_service import save_twitter_tweets_batch
from app.utils.twitter.normalizer import normalize_search_tweet_data

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
        search_batch.append({"phrase": phrase, "tweets": tweets})

    results = []
    seen_ids = set()
    logger.info(f"✅  seen_ids: {len(seen_ids)}")

    for batch in search_batch:
        for tweet in batch['tweets']:
            tweet_data = tweet.dict()
            tweet_dict = normalize_search_tweet_data(tweet_data)

            if tweet_dict['id'] and tweet_dict['id'] not in seen_ids:
                seen_ids.add(tweet_dict['id'])
                results.append(tweet_dict)

    # Save the unique tweets to the database
    if results:
        saved_tweets = await save_twitter_tweets_batch(supabase, results)
        return len(saved_tweets)

    return 0