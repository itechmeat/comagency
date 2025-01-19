from typing import Any, Callable
from loguru import logger
from fastapi import HTTPException
from app.services.twitter.client import twitter_client

class ExecutionStopError(Exception):
    pass

async def handle_twitter_request(func: Callable, *args: Any, **kwargs: Any) -> Any:
    """
    Generic handler for Twitter API requests with error handling and authentication

    Args:
        func: Async function that makes the actual Twitter API call
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        The result of the Twitter API call

    Raises:
        ExecutionStopError: On various errors that stop execution
        HTTPException: On various Twitter API errors with appropriate status codes
    """
    try:
        await twitter_client.ensure_authenticated()
        return await func(*args, **kwargs)
    except TypeError as e:
        logger.error(f"Type error in Twitter API request: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid request format: {str(e)}") from None
    except Exception as e:
        logger.error(f"Twitter API error: {str(e)}")
        raise ExecutionStopError(str(e)) from None