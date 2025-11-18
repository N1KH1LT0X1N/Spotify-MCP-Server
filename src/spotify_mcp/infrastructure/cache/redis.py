"""Redis cache implementation for distributed caching."""

import json
from typing import Any, Optional

try:
    import redis
    REDIS_INSTALLED = True
except ImportError:
    REDIS_INSTALLED = False
    redis = None

from .interface import CacheBackend


class RedisCache(CacheBackend):
    """
    Redis-based distributed cache.

    Features:
    - Distributed caching across multiple instances
    - Automatic serialization/deserialization
    - Native TTL support
    - High performance

    Requires: redis package (pip install redis)
    """

    def __init__(self, url: str = "redis://localhost:6379/0", decode_responses: bool = True):
        """
        Initialize Redis cache.

        Args:
            url: Redis connection URL
            decode_responses: Auto-decode responses to strings

        Raises:
            ImportError: If redis package not installed
        """
        if not REDIS_INSTALLED:
            raise ImportError(
                "Redis cache requires 'redis' package. "
                "Install with: pip install redis"
            )

        self._client = redis.from_url(url, decode_responses=decode_responses)
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        value = self._client.get(key)

        if value is None:
            self._misses += 1
            return None

        self._hits += 1
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # Return raw value if not JSON
            return value

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Store value in cache with TTL."""
        try:
            serialized = json.dumps(value, default=str)
        except (TypeError, ValueError):
            # Fallback to str representation
            serialized = str(value)

        self._client.setex(key, ttl, serialized)

    def delete(self, key: str) -> None:
        """Remove value from cache."""
        self._client.delete(key)

    def clear(self, pattern: str = "*") -> None:
        """Clear cache entries matching pattern."""
        cursor = 0
        while True:
            cursor, keys = self._client.scan(
                cursor=cursor,
                match=pattern,
                count=100
            )
            if keys:
                self._client.delete(*keys)
            if cursor == 0:
                break

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return self._client.exists(key) > 0

    def get_stats(self) -> dict:
        """Get cache statistics."""
        info = self._client.info('stats')
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

        return {
            'backend': 'redis',
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': f'{hit_rate:.2f}%',
            'total_requests': total_requests,
            'redis_version': self._client.info('server').get('redis_version'),
            'connected_clients': info.get('connected_clients', 0),
            'used_memory_human': self._client.info('memory').get('used_memory_human'),
        }

    def ping(self) -> bool:
        """
        Check Redis connection.

        Returns:
            True if connected, False otherwise
        """
        try:
            return self._client.ping()
        except Exception:
            return False

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        self._hits = 0
        self._misses = 0
