"""In-memory cache implementation using OrderedDict for LRU behavior."""

import fnmatch
import threading
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Any, Optional

from .interface import CacheBackend

# Optional metrics integration
try:
    from ..metrics import track_cache_operation, update_cache_metrics
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    track_cache_operation = lambda *args, **kwargs: None
    update_cache_metrics = lambda *args, **kwargs: None


class MemoryCache(CacheBackend):
    """
    Thread-safe in-memory cache with LRU eviction.

    Features:
    - LRU eviction when max_size reached
    - TTL-based expiration
    - Thread-safe operations
    - Hit/miss statistics
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize memory cache.

        Args:
            max_size: Maximum number of entries (default: 1000)
        """
        self._cache: OrderedDict = OrderedDict()
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                if METRICS_AVAILABLE:
                    track_cache_operation('get', 'miss')
                return None

            entry = self._cache[key]

            # Check expiration
            if entry['expires_at'] < datetime.utcnow():
                del self._cache[key]
                self._misses += 1
                if METRICS_AVAILABLE:
                    track_cache_operation('get', 'miss')
                return None

            # Move to end (LRU)
            self._cache.move_to_end(key)
            self._hits += 1
            if METRICS_AVAILABLE:
                track_cache_operation('get', 'hit')
                # Periodically update cache stats
                if self._hits % 100 == 0:  # Every 100 hits
                    update_cache_metrics('memory', self.get_stats())
            return entry['value']

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Store value in cache with TTL."""
        with self._lock:
            # Evict oldest if at capacity
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._cache.popitem(last=False)

            self._cache[key] = {
                'value': value,
                'expires_at': datetime.utcnow() + timedelta(seconds=ttl),
                'created_at': datetime.utcnow(),
            }
            self._cache.move_to_end(key)

            if METRICS_AVAILABLE:
                track_cache_operation('set', 'success')

    def delete(self, key: str) -> None:
        """Remove value from cache."""
        with self._lock:
            self._cache.pop(key, None)

    def clear(self, pattern: str = "*") -> None:
        """Clear cache entries matching pattern."""
        with self._lock:
            if pattern == "*":
                self._cache.clear()
            else:
                keys_to_delete = [
                    k for k in self._cache.keys()
                    if fnmatch.fnmatch(k, pattern)
                ]
                for key in keys_to_delete:
                    del self._cache[key]

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        with self._lock:
            if key not in self._cache:
                return False

            entry = self._cache[key]
            if entry['expires_at'] < datetime.utcnow():
                del self._cache[key]
                return False

            return True

    def get_stats(self) -> dict:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

            return {
                'backend': 'memory',
                'size': len(self._cache),
                'max_size': self._max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': f'{hit_rate:.2f}%',
                'total_requests': total_requests,
            }

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        with self._lock:
            self._hits = 0
            self._misses = 0
