import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel

from app.utils.twitter.decorators import handle_twitter_endpoint

router = APIRouter()
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class GenTextRequest(BaseModel):
    prompt: str
    model_name: str = 'llama-3.1-70b-versatile'

@router.post(
    "/gen_text",
    tags=["ai"],
    response_model=str,
    summary="Generate text",
    description="Sends a prompt to the specified text generation model and returns the text."
)
@handle_twitter_endpoint("generate text")
async def gen_text(request: GenTextRequest):
    prompt = request.prompt
    model_name = request.model_name

    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ API key not configured")
    
    model = GroqModel(model_name, api_key=GROQ_API_KEY)
    agent = Agent(model)

    result = await agent.run(prompt)

    if not result.data:
        raise HTTPException(status_code=500, detail="Model returned empty response")

    return result.data

# TODO: Add a character to the prompt
# TODO: Add more options for choosing the provider and model
# TODO: Create an enum for providers and models
# TODO: Add an options 'prefix' and 'suffix' with default twitter's texts for compile the final prompt
# TODO: Add an option for the language of the prompt
