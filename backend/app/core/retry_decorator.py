"""
Retry decorator for external API calls (Section 1.6.7)
Provides exponential backoff retry logic for transient failures
"""
import asyncio
import functools
import random
from typing import Any, Callable, Optional, Tuple, Type, Union
from app.core.logging import get_logger

logger = get_logger(__name__)


def retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None
):
    """
    Decorator that retries async functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Add random jitter to prevent thundering herd
        retryable_exceptions: Tuple of exception types to retry on (None = all)
    
    Example:
        @retry_with_exponential_backoff(max_retries=3, base_delay=1.0)
        async def fetch_data():
            return await api_client.get_data()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            attempt = 0
            last_exception = None
            
            while attempt <= max_retries:
                try:
                    # Log retry attempt if not first try
                    if attempt > 0:
                        logger.info(
                            f"Retry attempt {attempt}/{max_retries} for {func.__name__}"
                        )
                    
                    # Try to execute the function
                    result = await func(*args, **kwargs)
                    
                    # Success - log if it was a retry
                    if attempt > 0:
                        logger.info(
                            f"Successfully completed {func.__name__} after {attempt} retries"
                        )
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry this exception
                    if retryable_exceptions and not isinstance(e, retryable_exceptions):
                        logger.error(
                            f"Non-retryable exception in {func.__name__}: {str(e)}"
                        )
                        raise
                    
                    # Check if we've exhausted retries
                    if attempt >= max_retries:
                        logger.error(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}: {str(e)}"
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    # Add jitter if enabled
                    if jitter:
                        delay = delay * (0.5 + random.random())
                    
                    logger.warning(
                        f"Error in {func.__name__} (attempt {attempt + 1}/{max_retries + 1}): "
                        f"{str(e)}. Retrying in {delay:.2f} seconds..."
                    )
                    
                    # Wait before retrying
                    await asyncio.sleep(delay)
                    attempt += 1
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unexpected retry loop exit in {func.__name__}")
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            """Wrapper for synchronous functions."""
            attempt = 0
            last_exception = None
            
            while attempt <= max_retries:
                try:
                    if attempt > 0:
                        logger.info(
                            f"Retry attempt {attempt}/{max_retries} for {func.__name__}"
                        )
                    
                    result = func(*args, **kwargs)
                    
                    if attempt > 0:
                        logger.info(
                            f"Successfully completed {func.__name__} after {attempt} retries"
                        )
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if retryable_exceptions and not isinstance(e, retryable_exceptions):
                        logger.error(
                            f"Non-retryable exception in {func.__name__}: {str(e)}"
                        )
                        raise
                    
                    if attempt >= max_retries:
                        logger.error(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}: {str(e)}"
                        )
                        raise
                    
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    if jitter:
                        delay = delay * (0.5 + random.random())
                    
                    logger.warning(
                        f"Error in {func.__name__} (attempt {attempt + 1}/{max_retries + 1}): "
                        f"{str(e)}. Retrying in {delay:.2f} seconds..."
                    )
                    
                    import time
                    time.sleep(delay)
                    attempt += 1
            
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unexpected retry loop exit in {func.__name__}")
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Specialized retry decorators for specific use cases

def retry_api_call(max_retries: int = 3):
    """
    Retry decorator specifically for API calls.
    Retries on network errors, timeouts, and 5xx errors.
    """
    from aiohttp import ClientError, ServerError
    from requests.exceptions import RequestException, Timeout, ConnectionError
    
    return retry_with_exponential_backoff(
        max_retries=max_retries,
        base_delay=1.0,
        max_delay=30.0,
        retryable_exceptions=(
            ClientError,
            ServerError,
            RequestException,
            Timeout,
            ConnectionError,
            TimeoutError,
            OSError
        )
    )


def retry_database_operation(max_retries: int = 3):
    """
    Retry decorator specifically for database operations.
    Retries on connection errors and deadlocks.
    """
    from sqlalchemy.exc import OperationalError, DatabaseError, DisconnectionError
    from asyncpg.exceptions import PostgresConnectionError, DeadlockDetectedError
    
    return retry_with_exponential_backoff(
        max_retries=max_retries,
        base_delay=0.5,
        max_delay=10.0,
        retryable_exceptions=(
            OperationalError,
            DatabaseError,
            DisconnectionError,
            PostgresConnectionError,
            DeadlockDetectedError,
            ConnectionError
        )
    )