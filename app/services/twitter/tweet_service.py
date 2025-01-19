import asyncio
import os
from typing import Any, Dict, List

from loguru import logger
from twikit import Client

from app.models.schemas.tweet import DBTweet, TwitterTweet
from app.utils.twitter.normalizer import normalize_tweet_data

USE_TWITTER_MOCKS = os.getenv("USE_TWITTER_MOCKS", "false").lower() == "true"

ExecutionStopError = (asyncio.CancelledError, KeyboardInterrupt, SystemError)

async def save_twitter_tweet(supabase: Client, tweet_data: dict) -> DBTweet:
    try:
        twitter_tweet = TwitterTweet.model_validate(tweet_data)
        db_tweet = twitter_tweet.to_db_tweet()

        existing = supabase.table('tweets')\
            .select('*')\
            .eq('id', db_tweet.id)\
            .execute()

        if existing.data:
            logger.debug(f"Updating tweet {db_tweet.id}")
            update_data = {
                'id': db_tweet.id,
                'text': db_tweet.text,
                'author_id': db_tweet.author_id,
                'author_name': db_tweet.author_name,
                'author_username': db_tweet.author_username,
                'author_photo': db_tweet.author_photo,
                'lang': db_tweet.lang,
                'retweets_count': db_tweet.retweets_count,
                'likes_count': db_tweet.likes_count,
                'photo_urls': db_tweet.photo_urls,
                'media': db_tweet.media,
                'meta_data': db_tweet.meta_data,
                'updated_at': 'now()'
            }

            result = supabase.table('tweets')\
                .upsert(update_data, on_conflict='id')\
                .execute()
        else:
            logger.debug(f"Creating new tweet {db_tweet.id}")
            result = supabase.table('tweets')\
                .insert(db_tweet.model_dump())\
                .execute()

        if not result.data:
            raise Exception("No data returned from database operation")

        return DBTweet.model_validate(result.data[0])

    except Exception as e:
        logger.error(f"Error saving tweet: {str(e)}")
        raise Exception(f"Error saving tweet: {str(e)}") from e

async def save_twitter_tweets_batch(
    supabase: Client,
    tweets_data: List[Dict[Any, Any]],
    batch_size: int = 50
) -> List[DBTweet]:
    try:
        db_tweets = []
        for tweet_data in tweets_data:
            normalized_data = normalize_tweet_data(tweet_data)
            twitter_tweet = TwitterTweet.model_validate(normalized_data)
            db_tweets.append(twitter_tweet.to_db_tweet())

        tweet_ids = [tweet.id for tweet in db_tweets]
        existing_tweets = supabase.table('tweets')\
            .select('id')\
            .in_('id', tweet_ids)\
            .execute()

        existing_ids = set(tweet.get('id') for tweet in existing_tweets.data)

        updates = []
        inserts = []

        for db_tweet in db_tweets:
            tweet_dict = {
                'id': db_tweet.id,
                'text': db_tweet.text,
                'author_id': db_tweet.author_id,
                'author_name': db_tweet.author_name,
                'author_username': db_tweet.author_username,
                'author_photo': db_tweet.author_photo,
                'lang': db_tweet.lang,
                'retweets_count': db_tweet.retweets_count,
                'likes_count': db_tweet.likes_count,
                'photo_urls': db_tweet.photo_urls,
                'media': db_tweet.media,
                'meta_data': db_tweet.meta_data
            }

            if db_tweet.id in existing_ids:
                tweet_dict['updated_at'] = 'now()'
                updates.append(tweet_dict)
            else:
                inserts.append(tweet_dict)

        results = []

        for i in range(0, len(updates), batch_size):
            batch = updates[i:i + batch_size]
            if batch:
                logger.debug(f"Processing update batch {i // batch_size + 1}, size: {len(batch)}")
                result = supabase.table('tweets')\
                    .upsert(batch, on_conflict='id')\
                    .execute()
                results.extend(result.data)

        for i in range(0, len(inserts), batch_size):
            batch = inserts[i:i + batch_size]
            if batch:
                logger.debug(f"Processing insert batch {i // batch_size + 1}, size: {len(batch)}")
                result = supabase.table('tweets')\
                    .insert(batch)\
                    .execute()
                results.extend(result.data)

        return [DBTweet.model_validate(result) for result in results]

    except Exception as e:
        logger.error(f"Error in batch processing tweets: {str(e)}")
        raise Exception(f"Batch processing failed: {str(e)}") from e
