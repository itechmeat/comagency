import os
import stat
import uuid
from datetime import datetime

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel
from together import Together

from app.utils.twitter.decorators import handle_twitter_endpoint

router = APIRouter()
load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
BASE_IMAGE_DIR = os.path.join(os.path.dirname(__file__), "../../../assets/images")

client = Together(api_key=TOGETHER_API_KEY)

# Create a directory for today's date
today_date = datetime.now().strftime("%d-%m-%Y")
IMAGE_DIR = os.path.join(BASE_IMAGE_DIR, today_date)

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)
    # Set write permissions for the directory
    os.chmod(IMAGE_DIR, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

class GenImageRequest(BaseModel):
    prompt: str
    model_name: str = 'black-forest-labs/FLUX.1-schnell-Free'

@router.post(
    "/gen_image",
    tags=["ai"],
    response_model=dict,
    summary="Generate an image",
    description="Sends a prompt to the specified image generation model and returns the image."
)
@handle_twitter_endpoint("generate image")
async def gen_image(request: GenImageRequest):
    prompt = request.prompt
    model_name = request.model_name

    if not TOGETHER_API_KEY:
        raise HTTPException(status_code=500, detail="TOGETHER API key not configured")
    
    response = client.images.generate(
        prompt=prompt, model=model_name, steps=4
    )

    if not response.data or not response.data[0].url:
        raise HTTPException(status_code=500, detail="Model returned empty response")

    image_url = response.data[0].url
    
    try:
        async with httpx.AsyncClient() as http_client:
            image_response = await http_client.get(image_url)
            image_response.raise_for_status()
            
            file_extension = os.path.splitext(image_url)[1].split('/')[0].split('?')[0]
            if not file_extension:
                file_extension = '.jpg'
            file_name = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(IMAGE_DIR, file_name)  # Save in the date directory

            try:
                with open(file_path, "wb") as image_file:
                    image_file.write(image_response.content)
            except Exception as e:
                logger.error(f"Error saving image to {file_path}: {e}")
                raise HTTPException(status_code=500, detail=f"Error saving image: {e}") from e
            
            if not os.path.exists(file_path):
                logger.error(f"File was not created: {file_path}")
                raise HTTPException(status_code=500, detail=f"File was not created: {file_path}")
            else:
                logger.error(f"File created successfully: {file_path}")

            # Set write permissions for the file
            os.chmod(file_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            
            response_object = {
                "folder": today_date,
                "image": file_name,
                "path": f"{today_date}/{file_name}"
            }
            return response_object
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to download image: {e}") from e