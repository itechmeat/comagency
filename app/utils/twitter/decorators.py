from functools import wraps
from fastapi import HTTPException
from loguru import logger
from app.utils.twitter import ExecutionStopError

def handle_twitter_endpoint(operation_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ExecutionStopError:
                raise
            except Exception as e:
                error_msg = f"Failed to {operation_name}: {str(e)}"
                logger.error(error_msg)
                raise HTTPException(status_code=400, detail=str(e)) from None
        return wrapper
    return decorator