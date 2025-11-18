"""Graceful degradation with fallback chains."""

import asyncio
from typing import Callable, Any, Optional, List
from functools import wraps

from spotify_mcp.infrastructure.logging import get_logger

logger = get_logger(__name__)


class FallbackExhaustedError(Exception):
    """Raised when all fallback strategies have been exhausted."""
    pass


class Fallback:
    """
    Fallback strategy for graceful degradation.

    Allows defining multiple fallback strategies that are tried in order
    when the primary operation fails.
    """

    def __init__(self, name: str = "fallback"):
        """
        Initialize fallback strategy.

        Args:
            name: Name for logging and identification
        """
        self.name = name
        self.strategies: List[Callable] = []

        # Statistics
        self.total_executions = 0
        self.primary_successes = 0
        self.fallback_successes = 0
        self.total_failures = 0

    def add_strategy(self, strategy: Callable) -> 'Fallback':
        """
        Add a fallback strategy.

        Args:
            strategy: Async function to try as fallback

        Returns:
            Self for chaining
        """
        self.strategies.append(strategy)
        return self

    async def execute(
        self,
        primary: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute primary function with fallback strategies.

        Args:
            primary: Primary async function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Result from primary or fallback function

        Raises:
            FallbackExhaustedError: If all strategies failed
        """
        self.total_executions += 1
        last_exception = None

        # Try primary function first
        try:
            result = await primary(*args, **kwargs)
            self.primary_successes += 1
            return result

        except Exception as e:
            last_exception = e
            logger.warning(
                f"{self.name}: Primary function failed: {type(e).__name__}: {e}. "
                f"Trying {len(self.strategies)} fallback strategies..."
            )

        # Try fallback strategies in order
        for i, strategy in enumerate(self.strategies):
            try:
                logger.info(f"{self.name}: Trying fallback strategy {i + 1}/{len(self.strategies)}")
                result = await strategy(*args, **kwargs)

                self.fallback_successes += 1
                logger.info(
                    f"{self.name}: Fallback strategy {i + 1} succeeded",
                    extra={"fallback_index": i + 1}
                )

                return result

            except Exception as e:
                last_exception = e
                logger.warning(
                    f"{self.name}: Fallback strategy {i + 1} failed: "
                    f"{type(e).__name__}: {e}"
                )
                continue

        # All strategies exhausted
        self.total_failures += 1
        logger.error(
            f"{self.name}: All fallback strategies exhausted",
            exc_info=last_exception
        )

        raise FallbackExhaustedError(
            f"Primary function and {len(self.strategies)} fallback strategies all failed. "
            f"Last error: {type(last_exception).__name__}: {last_exception}"
        ) from last_exception

    def get_stats(self) -> dict:
        """Get fallback statistics."""
        return {
            "name": self.name,
            "total_executions": self.total_executions,
            "primary_successes": self.primary_successes,
            "fallback_successes": self.fallback_successes,
            "total_failures": self.total_failures,
            "primary_success_rate_percent": (
                (self.primary_successes / self.total_executions * 100)
                if self.total_executions > 0 else 0
            ),
            "fallback_usage_rate_percent": (
                (self.fallback_successes / self.total_executions * 100)
                if self.total_executions > 0 else 0
            ),
            "total_success_rate_percent": (
                ((self.primary_successes + self.fallback_successes) / self.total_executions * 100)
                if self.total_executions > 0 else 0
            ),
            "num_strategies": len(self.strategies)
        }


class FallbackChain:
    """
    Chainable fallback builder for fluent API.

    Usage:
        result = await (
            FallbackChain()
            .primary(fetch_from_spotify)
            .fallback(fetch_from_cache)
            .fallback(return_default_data)
            .execute(track_id)
        )
    """

    def __init__(self, name: str = "fallback_chain"):
        """
        Initialize fallback chain.

        Args:
            name: Name for logging
        """
        self._fallback = Fallback(name)
        self._primary: Optional[Callable] = None

    def primary(self, func: Callable) -> 'FallbackChain':
        """
        Set primary function.

        Args:
            func: Primary async function

        Returns:
            Self for chaining
        """
        self._primary = func
        return self

    def fallback(self, func: Callable) -> 'FallbackChain':
        """
        Add fallback function.

        Args:
            func: Fallback async function

        Returns:
            Self for chaining
        """
        self._fallback.add_strategy(func)
        return self

    async def execute(self, *args, **kwargs) -> Any:
        """
        Execute fallback chain.

        Args:
            *args: Arguments for functions
            **kwargs: Keyword arguments for functions

        Returns:
            Result from primary or fallback

        Raises:
            ValueError: If primary function not set
            FallbackExhaustedError: If all strategies failed
        """
        if self._primary is None:
            raise ValueError("Primary function not set. Call .primary() first.")

        return await self._fallback.execute(self._primary, *args, **kwargs)

    def get_stats(self) -> dict:
        """Get statistics."""
        return self._fallback.get_stats()


def with_fallback(
    *fallback_funcs: Callable,
    name: str = "fallback"
):
    """
    Decorator to add fallback strategies to a function.

    Usage:
        @with_fallback(fetch_from_cache, return_default_data, name="track_fetcher")
        async def fetch_track(track_id: str):
            return await spotify.get_track(track_id)

    Args:
        *fallback_funcs: Fallback functions to try in order
        name: Name for logging
    """
    fallback = Fallback(name)
    for func in fallback_funcs:
        fallback.add_strategy(func)

    def decorator(primary_func: Callable):
        @wraps(primary_func)
        async def wrapper(*args, **kwargs):
            return await fallback.execute(primary_func, *args, **kwargs)

        # Attach fallback to function for introspection
        wrapper.fallback = fallback

        return wrapper

    return decorator


# Common fallback strategies

async def return_none(*args, **kwargs) -> None:
    """Fallback that returns None."""
    logger.debug("Using return_none fallback")
    return None


async def return_empty_dict(*args, **kwargs) -> dict:
    """Fallback that returns empty dict."""
    logger.debug("Using return_empty_dict fallback")
    return {}


async def return_empty_list(*args, **kwargs) -> list:
    """Fallback that returns empty list."""
    logger.debug("Using return_empty_list fallback")
    return []


async def return_error_response(error_message: str = "Service unavailable") -> dict:
    """
    Fallback that returns error response.

    Args:
        error_message: Error message to include

    Returns:
        Error response dict
    """
    logger.debug(f"Using return_error_response fallback: {error_message}")
    return {
        "error": error_message,
        "status": "degraded",
        "fallback": True
    }


def cache_fallback(cache_manager, cache_key: str):
    """
    Create a fallback that fetches from cache.

    Args:
        cache_manager: Cache manager instance
        cache_key: Key to fetch from cache

    Returns:
        Async fallback function
    """
    async def _cache_fallback(*args, **kwargs):
        logger.info(f"Using cache fallback for key: {cache_key}")
        cached_value = await cache_manager.get(cache_key)

        if cached_value is not None:
            logger.info(f"Cache fallback succeeded for key: {cache_key}")
            return cached_value

        raise Exception(f"No cached value for key: {cache_key}")

    return _cache_fallback


def default_value_fallback(default_value: Any):
    """
    Create a fallback that returns a default value.

    Args:
        default_value: Value to return

    Returns:
        Async fallback function
    """
    async def _default_fallback(*args, **kwargs):
        logger.info(f"Using default value fallback: {default_value}")
        return default_value

    return _default_fallback
