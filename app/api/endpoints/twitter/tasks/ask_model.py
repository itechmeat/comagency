import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from app.utils.twitter.decorators import handle_twitter_endpoint

router = APIRouter()
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@router.post(
    "/tasks/ask-model",
    tags=["tasks"],
    response_model=str,
    summary="Ask a question to the language model",
    description="Sends a prompt to the specified language model and returns the response."
)
@handle_twitter_endpoint("ask model")
async def ask_model(prompt: str, model_name: str = 'llama-3.1-70b-versatile'):
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
