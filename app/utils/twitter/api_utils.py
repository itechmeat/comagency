from typing import Any, Callable
from loguru import logger
from fastapi import HTTPException
from twikit import (
    TooManyRequests, Unauthorized, TwitterException, 
    BadRequest, Forbidden, NotFound, RequestTimeout, 
    ServerError, AccountLocked
)
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
        return await func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Twitter API error: {str(e)}")
        raise ExecutionStopError(str(e)) from None

async def handle_twitter_request_old(request_func):
    """
    Generic handler for Twitter API requests with error handling and authentication
    
    Args:
        request_func: Async function that makes the actual Twitter API call
        
    Returns:
        The result of the Twitter API call
        
    Raises:
        HTTPException: On various Twitter API errors with appropriate status codes
    """
    try:
        await twitter_client.ensure_authenticated()
        return await request_func()
    except ExecutionStopError:
        raise
    except TooManyRequests:
        raise HTTPException(status_code=429, detail="Rate limit reached") from None
    except Unauthorized:
        # Try to re-authenticate once
        try:
            await twitter_client.authenticate()
            return await request_func()
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}") from None
    except (AccountLocked, BadRequest, Forbidden, NotFound, TwitterException) as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
    except (RequestTimeout, ServerError):
        raise HTTPException(status_code=503, detail="Service temporarily unavailable") from None