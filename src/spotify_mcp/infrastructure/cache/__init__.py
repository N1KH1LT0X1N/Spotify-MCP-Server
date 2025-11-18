"""
Caching infrastructure for Spotify MCP Server.

Provides multi-tier caching with:
- Memory cache (default, no dependencies)
- Redis cache (optional, for distributed caching)
- Configurable TTL strategies by data type
- Transparent integration via decorators
"""

from .interface import CacheBackend
from .memory import MemoryCache
from .manager import CacheManager, get_cache_manager
from .strategies import CacheStrategy, CacheKeyGenerator

# Try to import Redis cache if available
try:
    from .redis import RedisCache
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    RedisCache = None

__all__ = [
    'CacheBackend',
    'MemoryCache',
    'RedisCache',
    'CacheManager',
    'get_cache_manager',
    'CacheStrategy',
    'CacheKeyGenerator',
    'REDIS_AVAILABLE',
]
