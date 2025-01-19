import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from app.utils.twitter.decorators import handle_twitter_endpoint

router = APIRouter()
load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

@router.post(
    "/gen_text_together",
    tags=["ai"],
    response_model=str,
    summary="Generate text with Together",
    description="Sends a prompt to the specified text generation model and returns the text."
)
@handle_twitter_endpoint("generate text")
async def gen_text_together(prompt: str, model_name: str = 'meta-llama/Llama-3.3-70B-Instruct-Turbo'):
    if not TOGETHER_API_KEY:
        raise HTTPException(status_code=500, detail="TOGETHER API key not configured")
    
    model = OpenAIModel(
        model_name,
        base_url='https://api.together.xyz/v1',
        api_key=TOGETHER_API_KEY,
    )
    agent = Agent(model)

    result = await agent.run(prompt)

    if not result.data:
        raise HTTPException(status_code=500, detail="Model returned empty response")

    return result.data