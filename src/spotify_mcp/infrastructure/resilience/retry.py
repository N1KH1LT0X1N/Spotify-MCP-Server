"""Retry logic with exponential backoff and jitter."""

import asyncio
import random
import time
from typing import Callable, Any, Optional, Type, Tuple
from functools import wraps

from spotify_mcp.infrastructure.logging import get_logger

logger = get_logger(__name__)

# Optional metrics integration
try:
    from spotify_mcp.infrastructure.metrics import get_metrics_collector
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False


class RetryExhaustedError(Exception):
    """Raised when all retry attempts have been exhausted."""
    pass


class RetryPolicy:
    """
    Retry policy with exponential backoff and jitter.

    Implements industry best practices for retries:
    - Exponential backoff to avoid thundering herd
    - Jitter to prevent synchronized retries
    - Max retry limits
    - Configurable backoff multipliers
    """

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None
    ):
        """
        Initialize retry policy.

        Args:
            max_attempts: Maximum number of retry attempts (including first try)
            initial_delay: Initial delay in seconds before first retry
            max_delay: Maximum delay in seconds between retries
            exponential_base: Base for exponential backoff (2.0 = double each time)
            jitter: Add random jitter to avoid thundering herd
            retryable_exceptions: Tuple of exception types to retry (None = retry all)
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or (Exception,)

        # Statistics
        self.total_attempts = 0
        self.total_retries = 0
        self.total_successes = 0
        self.total_failures = 0

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number.

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff: initial_delay * (base ^ attempt)
        delay = self.initial_delay * (self.exponential_base ** attempt)

        # Cap at max_delay
        delay = min(delay, self.max_delay)

        # Add jitter (randomize between 0 and delay)
        if self.jitter:
            delay = random.uniform(0, delay)

        return delay

    def is_retryable(self, exception: Exception) -> bool:
        """
        Check if exception is retryable.

        Args:
            exception: Exception that occurred

        Returns:
            True if should retry
        """
        return isinstance(exception, self.retryable_exceptions)

    async def execute(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with retry logic.

        Args:
            func: Async function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            RetryExhaustedError: If all retry attempts failed
            Any non-retryable exception raised by function
        """
        last_exception = None

        for attempt in range(self.max_attempts):
            self.total_attempts += 1

            try:
                # Execute function
                result = await func(*args, **kwargs)

                self.total_successes += 1

                if attempt > 0:
                    logger.info(
                        f"Retry succeeded on attempt {attempt + 1}/{self.max_attempts}"
                    )

                return result

            except Exception as e:
                last_exception = e

                # Check if exception is retryable
                if not self.is_retryable(e):
                    logger.debug(
                        f"Non-retryable exception: {type(e).__name__}: {e}"
                    )
                    self.total_failures += 1
                    raise

                # Check if we have more attempts
                if attempt >= self.max_attempts - 1:
                    self.total_failures += 1
                    logger.error(
                        f"All {self.max_attempts} retry attempts exhausted",
                        exc_info=True
                    )
                    raise RetryExhaustedError(
                        f"Failed after {self.max_attempts} attempts. "
                        f"Last error: {type(e).__name__}: {e}"
                    ) from e

                # Calculate delay and retry
                delay = self.calculate_delay(attempt)
                self.total_retries += 1

                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_attempts} failed: "
                    f"{type(e).__name__}: {e}. "
                    f"Retrying in {delay:.2f}s...",
                    extra={
                        "attempt": attempt + 1,
                        "max_attempts": self.max_attempts,
                        "delay_seconds": delay,
                        "exception_type": type(e).__name__
                    }
                )

                await asyncio.sleep(delay)

    def get_stats(self) -> dict:
        """Get retry statistics."""
        return {
            "total_attempts": self.total_attempts,
            "total_retries": self.total_retries,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "retry_rate_percent": (
                (self.total_retries / self.total_attempts * 100)
                if self.total_attempts > 0 else 0
            ),
            "success_rate_percent": (
                (self.total_successes / self.total_attempts * 100)
                if self.total_attempts > 0 else 0
            ),
            "config": {
                "max_attempts": self.max_attempts,
                "initial_delay": self.initial_delay,
                "max_delay": self.max_delay,
                "exponential_base": self.exponential_base,
                "jitter": self.jitter
            }
        }


# Common retry policies for different scenarios

# Spotify API retry policy - for transient network errors
SPOTIFY_API_RETRY_POLICY = RetryPolicy(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=10.0,
    exponential_base=2.0,
    jitter=True,
    retryable_exceptions=(
        ConnectionError,
        TimeoutError,
        # Add Spotify-specific errors here
    )
)

# Aggressive retry for critical operations
CRITICAL_RETRY_POLICY = RetryPolicy(
    max_attempts=5,
    initial_delay=0.5,
    max_delay=30.0,
    exponential_base=2.0,
    jitter=True
)

# Fast retry for quick operations
QUICK_RETRY_POLICY = RetryPolicy(
    max_attempts=2,
    initial_delay=0.1,
    max_delay=1.0,
    exponential_base=2.0,
    jitter=False
)


def retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None
):
    """
    Decorator for automatic retry with exponential backoff.

    Usage:
        @retry(max_attempts=3, initial_delay=1.0)
        async def fetch_data():
            return await client.get_track(track_id)

    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Add random jitter
        retryable_exceptions: Tuple of exception types to retry
    """
    policy = RetryPolicy(
        max_attempts=max_attempts,
        initial_delay=initial_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        retryable_exceptions=retryable_exceptions
    )

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await policy.execute(func, *args, **kwargs)

        # Attach policy to function for introspection
        wrapper.retry_policy = policy

        return wrapper

    return decorator


# Global retry policy registry
_retry_policies: dict[str, RetryPolicy] = {}


def register_retry_policy(name: str, policy: RetryPolicy) -> None:
    """Register a named retry policy."""
    _retry_policies[name] = policy


def get_retry_policy(name: str) -> Optional[RetryPolicy]:
    """Get a named retry policy."""
    return _retry_policies.get(name)


# Register default policies
register_retry_policy("spotify_api", SPOTIFY_API_RETRY_POLICY)
register_retry_policy("critical", CRITICAL_RETRY_POLICY)
register_retry_policy("quick", QUICK_RETRY_POLICY)
