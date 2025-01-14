from pydantic import BaseModel
from typing import List

class TweetData(BaseModel):
    tweet_id: str
    tweet_user_name: str
    tweet_user_nick: str
    text: str
    created_at: str
    retweets: int
    likes: int
    photo_urls: List[str]
    tweet_lang: str

class TimelineParams(BaseModel):
    minimum_tweets: int = 10

class SearchParams(BaseModel):
    query: str
    minimum_tweets: int = 10

class SearchResponse(BaseModel):
    tweets: List[TweetData]
    status: str = "success"
