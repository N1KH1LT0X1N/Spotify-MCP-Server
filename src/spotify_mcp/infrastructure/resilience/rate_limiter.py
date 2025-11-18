"""Rate limiting using token bucket algorithm."""

import asyncio
import time
from typing import Optional
from datetime import datetime

from spotify_mcp.infrastructure.logging import get_logger

logger = get_logger(__name__)


class TokenBucket:
    """
    Token bucket rate limiter implementation.

    Tokens are added to the bucket at a constant rate. Each request
    consumes a token. If no tokens are available, the request waits.
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket.

        Args:
            capacity: Maximum number of tokens in bucket
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill_time = time.time()
        self.lock = asyncio.Lock()

        # Statistics
        self.total_requests = 0
        self.total_throttled = 0
        self.total_wait_time = 0.0

    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens from bucket (wait if not available).

        Args:
            tokens: Number of tokens to acquire

        Returns:
            Wait time in seconds (0 if no wait)
        """
        async with self.lock:
            self.total_requests += 1

            # Refill tokens based on time elapsed
            self._refill()

            # If enough tokens, consume and return
            if self.tokens >= tokens:
                self.tokens -= tokens
                return 0.0

            # Calculate wait time needed
            tokens_needed = tokens - self.tokens
            wait_time = tokens_needed / self.refill_rate

            self.total_throttled += 1
            self.total_wait_time += wait_time

            logger.debug(
                f"Rate limited: waiting {wait_time:.2f}s for {tokens_needed} tokens"
            )

        # Wait outside the lock
        await asyncio.sleep(wait_time)

        # Acquire tokens after waiting
        async with self.lock:
            self._refill()
            self.tokens -= tokens

        return wait_time

    def try_acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens without waiting.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            True if acquired, False if not enough tokens
        """
        self.total_requests += 1
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True

        self.total_throttled += 1
        return False

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill_time

        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill_time = now

    def get_stats(self) -> dict:
        """Get token bucket statistics."""
        return {
            "available_tokens": int(self.tokens),
            "capacity": self.capacity,
            "refill_rate": self.refill_rate,
            "total_requests": self.total_requests,
            "total_throttled": self.total_throttled,
            "throttle_rate_percent": (
                (self.total_throttled / self.total_requests * 100)
                if self.total_requests > 0 else 0
            ),
            "total_wait_time_seconds": self.total_wait_time,
            "average_wait_time_seconds": (
                (self.total_wait_time / self.total_throttled)
                if self.total_throttled > 0 else 0
            )
        }

    def reset(self) -> None:
        """Reset token bucket to full capacity."""
        self.tokens = self.capacity
        self.last_refill_time = time.time()
        self.total_requests = 0
        self.total_throttled = 0
        self.total_wait_time = 0.0


class RateLimiter:
    """
    Multi-tier rate limiter for Spotify API.

    Implements rate limiting at multiple time scales:
    - Per-second limits (burst protection)
    - Per-minute limits (sustained traffic)
    - Per-hour limits (overall quota)
    """

    def __init__(
        self,
        requests_per_second: int = 10,
        requests_per_minute: int = 100,
        requests_per_hour: int = 1000
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_second: Max requests per second
            requests_per_minute: Max requests per minute
            requests_per_hour: Max requests per hour
        """
        self.per_second = TokenBucket(
            capacity=requests_per_second,
            refill_rate=requests_per_second
        )

        self.per_minute = TokenBucket(
            capacity=requests_per_minute,
            refill_rate=requests_per_minute / 60
        )

        self.per_hour = TokenBucket(
            capacity=requests_per_hour,
            refill_rate=requests_per_hour / 3600
        )

    async def acquire(self) -> dict:
        """
        Acquire rate limit permission (wait if necessary).

        Returns:
            Dictionary with wait times for each tier
        """
        wait_times = {
            "per_second": await self.per_second.acquire(),
            "per_minute": await self.per_minute.acquire(),
            "per_hour": await self.per_hour.acquire()
        }

        total_wait = sum(wait_times.values())

        if total_wait > 0:
            logger.info(
                f"Rate limited: total wait {total_wait:.2f}s",
                extra=wait_times
            )

        return {
            "wait_times": wait_times,
            "total_wait_seconds": total_wait
        }

    def try_acquire(self) -> bool:
        """
        Try to acquire rate limit permission without waiting.

        Returns:
            True if acquired, False if rate limited
        """
        if not self.per_second.try_acquire():
            return False
        if not self.per_minute.try_acquire():
            return False
        if not self.per_hour.try_acquire():
            return False

        return True

    def get_stats(self) -> dict:
        """Get rate limiter statistics for all tiers."""
        return {
            "per_second": self.per_second.get_stats(),
            "per_minute": self.per_minute.get_stats(),
            "per_hour": self.per_hour.get_stats()
        }

    def reset(self) -> None:
        """Reset all rate limit tiers."""
        self.per_second.reset()
        self.per_minute.reset()
        self.per_hour.reset()


class SpotifyRateLimiter(RateLimiter):
    """
    Rate limiter specifically configured for Spotify API limits.

    Spotify API rate limits (as of 2024):
    - ~180 requests per minute (web API)
    - Rate limit headers in responses
    """

    def __init__(self):
        """Initialize Spotify-specific rate limiter."""
        super().__init__(
            requests_per_second=10,  # Conservative burst limit
            requests_per_minute=150,  # Below Spotify's ~180 limit
            requests_per_hour=5000   # Well below typical hourly limits
        )

        # Track Spotify API rate limit headers
        self.api_rate_limit_remaining: Optional[int] = None
        self.api_rate_limit_reset: Optional[datetime] = None

    def update_from_headers(self, headers: dict) -> None:
        """
        Update rate limits based on Spotify API response headers.

        Args:
            headers: HTTP response headers from Spotify API
        """
        # Spotify uses X-RateLimit-* headers
        if "X-RateLimit-Remaining" in headers:
            try:
                self.api_rate_limit_remaining = int(headers["X-RateLimit-Remaining"])
            except (ValueError, TypeError):
                pass

        if "X-RateLimit-Reset" in headers:
            try:
                reset_timestamp = int(headers["X-RateLimit-Reset"])
                self.api_rate_limit_reset = datetime.fromtimestamp(reset_timestamp)
            except (ValueError, TypeError):
                pass

    def get_api_rate_limit_status(self) -> dict:
        """Get Spotify API rate limit status from headers."""
        return {
            "remaining": self.api_rate_limit_remaining,
            "reset": self.api_rate_limit_reset.isoformat() if self.api_rate_limit_reset else None,
            "seconds_until_reset": (
                (self.api_rate_limit_reset - datetime.utcnow()).total_seconds()
                if self.api_rate_limit_reset else None
            )
        }


# Global rate limiter instance
_rate_limiter: Optional[SpotifyRateLimiter] = None


def get_rate_limiter() -> SpotifyRateLimiter:
    """
    Get global rate limiter instance (singleton pattern).

    Returns:
        Global Spotify rate limiter
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = SpotifyRateLimiter()
    return _rate_limiter


def init_rate_limiter(
    requests_per_second: int = 10,
    requests_per_minute: int = 150,
    requests_per_hour: int = 5000
) -> SpotifyRateLimiter:
    """
    Initialize global rate limiter with custom limits.

    Args:
        requests_per_second: Max requests per second
        requests_per_minute: Max requests per minute
        requests_per_hour: Max requests per hour

    Returns:
        Configured rate limiter
    """
    global _rate_limiter
    _rate_limiter = SpotifyRateLimiter()
    _rate_limiter.per_second = TokenBucket(requests_per_second, requests_per_second)
    _rate_limiter.per_minute = TokenBucket(requests_per_minute, requests_per_minute / 60)
    _rate_limiter.per_hour = TokenBucket(requests_per_hour, requests_per_hour / 3600)
    return _rate_limiter
