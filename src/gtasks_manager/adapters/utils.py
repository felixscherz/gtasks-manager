import random
import time
from typing import Any, Callable

from googleapiclient.errors import HttpError

from gtasks_manager.core.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


def execute_with_retry(request_func: Callable[[], Any], max_retries: int = 3) -> Any:
    """Execute API request with exponential backoff and error translation."""
    for attempt in range(max_retries + 1):
        try:
            return request_func().execute()
        except HttpError as error:
            status = error.resp.status

            # Handle errors that shouldn't be retried
            if status == 401 or status == 403:
                raise AuthenticationError(f"Authentication failed: {error}")
            if status == 404:
                raise NotFoundError(f"Resource not found: {error}")
            if status == 400:
                raise ValidationError(f"Invalid request: {error}")

            # Handle rate limiting and server errors with retry
            if status == 429 or status >= 500:
                if attempt == max_retries:
                    if status == 429:
                        raise RateLimitError("Rate limit exceeded")
                    raise APIError(f"API request failed after {max_retries} retries: {error}")

                # Exponential backoff: 1s, 2s, 4s...
                wait = (2**attempt) + (random.random() * 0.1)
                time.sleep(wait)
                continue

            # Other errors
            raise APIError(f"An unexpected API error occurred: {error}")
        except Exception as e:
            raise APIError(f"An unexpected error occurred: {e}")
