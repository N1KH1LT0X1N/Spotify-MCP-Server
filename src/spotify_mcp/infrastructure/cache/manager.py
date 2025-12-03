"""Cache manager for backend selection and configuration."""

import os
import sys
import io
from typing import Optional

# Force UTF-8 encoding for Windows console compatibility
# BUT ONLY if not running as MCP server (which uses stdin/stdout for JSON-RPC)
if sys.platform == 'win32' and sys.stdin.isatty() and hasattr(sys.stdout, 'buffer'):
    try:
        # Only wrap if not already wrapped and if buffer is available
        if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        if not isinstance(sys.stderr, io.TextIOWrapper) or sys.stderr.encoding != 'utf-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except (AttributeError, io.UnsupportedOperation, ValueError):
        pass

from .interface import CacheBackend
from .memory import MemoryCache

# Try to import Redis
try:
    from .redis import RedisCache
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    RedisCache = None


class CacheManager:
    """
    Manages cache backend selection and configuration.

    Automatically selects the best available cache backend:
    1. Redis (if configured and available)
    2. Memory (default fallback)
    """

    def __init__(
        self,
        backend: Optional[str] = None,
        redis_url: Optional[str] = None,
        max_memory_size: int = 1000,
    ):
        """
        Initialize cache manager.

        Args:
            backend: Cache backend ('memory' or 'redis'). If None, auto-detect.
            redis_url: Redis connection URL (default: from env or localhost)
            max_memory_size: Max entries for memory cache (default: 1000)
        """
        self._backend_name = backend or os.getenv('CACHE_BACKEND', 'memory')
        self._redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self._max_memory_size = max_memory_size
        self._cache: Optional[CacheBackend] = None

    @property
    def cache(self) -> CacheBackend:
        """
        Get cache backend instance (lazy initialization).

        Returns:
            Configured cache backend
        """
        if self._cache is None:
            self._cache = self._create_backend()
        return self._cache

    def _create_backend(self) -> CacheBackend:
        """
        Create cache backend based on configuration.

        Returns:
            Cache backend instance
        """
        if self._backend_name == 'redis':
            if not REDIS_AVAILABLE:
                print("Warning: Redis cache requested but redis package not installed. "
                      "Falling back to memory cache. Install with: pip install redis")
                return MemoryCache(max_size=self._max_memory_size)

            try:
                cache = RedisCache(url=self._redis_url)
                # Test connection
                if not cache.ping():
                    print(f"Warning: Cannot connect to Redis at {self._redis_url}. "
                          f"Falling back to memory cache.")
                    return MemoryCache(max_size=self._max_memory_size)
                print(f"✓ Using Redis cache: {self._redis_url}")
                return cache
            except Exception as e:
                print(f"Warning: Redis cache initialization failed: {e}. "
                      f"Falling back to memory cache.")
                return MemoryCache(max_size=self._max_memory_size)

        # Default to memory cache
        print(f"✓ Using memory cache (max_size={self._max_memory_size})")
        return MemoryCache(max_size=self._max_memory_size)

    def get_stats(self) -> dict:
        """Get cache statistics."""
        return self.cache.get_stats()

    def clear(self, pattern: str = "*") -> None:
        """Clear cache entries matching pattern."""
        self.cache.clear(pattern)

    def reset_stats(self) -> None:
        """Reset statistics if supported by backend."""
        if hasattr(self.cache, 'reset_stats'):
            self.cache.reset_stats()


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """
    Get global cache manager instance (singleton pattern).

    Returns:
        Global cache manager
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def init_cache(
    backend: Optional[str] = None,
    redis_url: Optional[str] = None,
    max_memory_size: int = 1000,
) -> CacheManager:
    """
    Initialize global cache manager with custom configuration.

    Args:
        backend: Cache backend ('memory' or 'redis')
        redis_url: Redis connection URL
        max_memory_size: Max entries for memory cache

    Returns:
        Configured cache manager
    """
    global _cache_manager
    _cache_manager = CacheManager(
        backend=backend,
        redis_url=redis_url,
        max_memory_size=max_memory_size,
    )
    return _cache_manager
