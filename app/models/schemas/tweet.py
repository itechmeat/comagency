from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TweetAuthor(BaseModel):
    id: str
    name: str
    username: str
    profile_image_url: Optional[str] = None

class TweetDetails(BaseModel):
    id: str
    text: str
    display_text: str
    created_at: str
    lang: str
    retweet_count: int
    favorite_count: int
    author: TweetAuthor
    in_reply_to_status_id: Optional[str] = None
    in_reply_to_user_id: Optional[str] = None
    in_reply_to_screen_name: Optional[str] = None
    in_reply_to: Optional[str] = None
    photo_urls: List[str] = []
    media: List[Dict[str, Any]] = Field(default_factory=list)

class TweetThread(BaseModel):
    main_tweet: TweetDetails
    replies: List[TweetDetails] 

class CreateTweetRequest(BaseModel):
    text: str
    reply_to: Optional[str] = None

class HandleMentionLLMResponse(BaseModel):
    target_tweet_id: str
    reply_text: str

# Database models

class TwitterAuthor(BaseModel):
    id: str
    name: str
    username: str
    profile_image_url: Optional[str] = None

class TwitterTweet(BaseModel):
    id: str
    text: str
    display_text: str
    lang: str
    retweet_count: int
    favorite_count: int
    author: TwitterAuthor
    in_reply_to_status_id: Optional[str] = None
    in_reply_to_user_id: Optional[str] = None
    in_reply_to_screen_name: Optional[str] = None
    in_reply_to: Optional[str] = None
    photo_urls: List[str] = Field(default_factory=list)
    media: List[Dict[str, Any]] = Field(default_factory=list)

    def to_db_tweet(self) -> 'DBTweetCreate':
        return DBTweetCreate(
            id=self.id,
            text=self.text,
            author_id=self.author.id,
            author_name=self.author.name,
            author_username=self.author.username,
            author_photo=self.author.profile_image_url,
            lang=self.lang,
            retweets_count=self.retweet_count,
            likes_count=self.favorite_count,
            photo_urls=self.photo_urls,
            media=self.media,
            meta_data={
                "display_text": self.display_text,
                "in_reply_to_status_id": self.in_reply_to_status_id,
                "in_reply_to_user_id": self.in_reply_to_user_id,
                "in_reply_to_screen_name": self.in_reply_to_screen_name,
                "in_reply_to": self.in_reply_to
            }
        )

class DBTweetBase(BaseModel):
    text: str
    author_id: str
    author_name: str
    author_username: str
    author_photo: Optional[str] = None
    lang: str = "en"
    retweets_count: int = 0
    likes_count: int = 0
    photo_urls: List[str] = Field(default_factory=list)
    meta_data: dict = Field(default_factory=dict)
    search_query_by: str = ""
    search_text_by: str = ""
    media: List[Dict[str, Any]] = Field(default_factory=list)

class DBTweetCreate(DBTweetBase):
    id: str

class DBTweetUpdate(BaseModel):
    is_processed: Optional[bool] = None
    is_liked: Optional[bool] = None
    is_no_reply: Optional[bool] = None
    sentiment: Optional[str] = None
    reply_id: Optional[str] = None
    retweets_count: Optional[int] = None
    likes_count: Optional[int] = None
    meta_data: Optional[dict] = None

class DBTweet(DBTweetBase):
    id: str
    created_at: datetime
    updated_at: datetime
    reply_id: Optional[str] = None
    is_processed: bool = False
    is_liked: bool = False
    is_no_reply: bool = False
    sentiment: str = ""

    class Config:
        from_attributes = True