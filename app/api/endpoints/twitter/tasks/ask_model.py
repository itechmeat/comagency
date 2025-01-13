import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from app.models.schemas.tweet import TweetDetails
from app.utils.twitter.decorators import handle_twitter_endpoint
from ..tweets.single_tweet import get_tweet_by_id
from ..tweets.new import create_tweet
from ..tweets.like import like_tweet

router = APIRouter()
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@router.post(
    "/tasks/ask-model",
    tags=["tasks"],
    response_model=str,
    summary="Ask model",
    description="Ask model"
)
@handle_twitter_endpoint("ask model")
async def ask_model(prompt: str):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ API key not configured")
    
    model = GroqModel('llama-3.1-70b-versatile', api_key=GROQ_API_KEY)
    agent = Agent(model)

    result = await agent.run(prompt)

    if not result.data:
        raise HTTPException(status_code=500, detail="Model returned empty response")

    return result.data