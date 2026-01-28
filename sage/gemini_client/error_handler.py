"""Error handling for Gemini API calls."""
import time
from typing import Callable, Any
from functools import wraps
from loguru import logger


class GeminiAPIError(Exception):
    """Base exception for Gemini API errors."""
    pass


class RateLimitError(GeminiAPIError):
    """Rate limit exceeded."""
    pass


class AuthenticationError(GeminiAPIError):
    """Authentication failed."""
    pass


class InvalidRequestError(GeminiAPIError):
    """Invalid request parameters."""
    pass


class ServiceUnavailableError(GeminiAPIError):
    """Gemini service unavailable."""
    pass


def retry_on_error(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    retry_on: tuple = (ServiceUnavailableError, RateLimitError)
):
    """Decorator to retry function on specific errors.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
        retry_on: Tuple of exception types to retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except retry_on as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        wait_time = backoff_factor ** attempt
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {wait_time}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")
                        raise
                        
                except Exception as e:
                    # Don't retry on other exceptions
                    logger.error(f"Non-retryable error: {e}")
                    raise
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


def handle_api_error(error: Exception) -> GeminiAPIError:
    """Convert API errors to custom exceptions.
    
    Args:
        error: Original exception
        
    Returns:
        Custom GeminiAPIError
    """
    error_str = str(error).lower()
    
    if "rate limit" in error_str or "quota" in error_str:
        return RateLimitError(f"Rate limit exceeded: {error}")
    
    elif "authentication" in error_str or "api key" in error_str:
        return AuthenticationError(f"Authentication failed: {error}")
    
    elif "invalid" in error_str or "bad request" in error_str:
        return InvalidRequestError(f"Invalid request: {error}")
    
    elif "unavailable" in error_str or "503" in error_str:
        return ServiceUnavailableError(f"Service unavailable: {error}")
    
    else:
        return GeminiAPIError(f"API error: {error}")
