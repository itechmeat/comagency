class TweetRepository:
    async def get_tweet_by_id(self, tweet_id: str):
        result = supabase.table('tweets').select('*').eq('tweet_id', tweet_id).execute()
        return result.data[0] if result.data else None

    async def get_tweets_by_username(self, username: str, limit: int):
        result = supabase.table('tweets').select('*').eq('tweet_user_name', username).limit(limit).execute()
        return result.data if result.data else []