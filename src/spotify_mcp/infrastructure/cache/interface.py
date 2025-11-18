"""Base interface for cache backends."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """
        Store value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 5 minutes)
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Remove value from cache.

        Args:
            key: Cache key
        """
        pass

    @abstractmethod
    def clear(self, pattern: str = "*") -> None:
        """
        Clear cache entries matching pattern.

        Args:
            pattern: Pattern to match keys (default: all keys)
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists and not expired
        """
        pass

    @abstractmethod
    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats (hits, misses, size, etc.)
        """
        pass
