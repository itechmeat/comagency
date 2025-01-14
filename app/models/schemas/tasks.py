from pydantic import BaseModel, Field
from typing import Optional

class HandleMentionRequest(BaseModel):
    tweet_id: str = Field(default="1879067214780977396", description="ID of the tweet to handle")
    limit: Optional[int] = 100