"""Cache decorators for transparent caching integration."""

import functools
import hashlib
import json
from typing import Any, Callable, Optional

from .manager import get_cache_manager
from .strategies import CacheStrategy


def cached(strategy: CacheStrategy):
    """
    Decorator to cache function results.

    Args:
        strategy: Cache strategy defining TTL and key prefix

    Usage:
        @cached(CacheStrategy.TRACK_METADATA)
        def get_track(self, track_id: str):
            return self.sp.track(track_id)

    The decorator:
    - Generates cache key from function name and arguments
    - Checks cache before calling function
    - Stores result in cache with appropriate TTL
    - Returns cached value on subsequent calls
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            cache = get_cache_manager().cache

            # Generate cache key from function and arguments
            cache_key = _generate_cache_key(func, strategy.prefix, args, kwargs)

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = func(self, *args, **kwargs)

            # Store in cache if result is not None
            if result is not None:
                cache.set(cache_key, result, ttl=strategy.ttl)

            return result

        # Add cache_key method to wrapper for testing/debugging
        wrapper.get_cache_key = lambda *args, **kwargs: _generate_cache_key(
            func, strategy.prefix, args, kwargs
        )

        return wrapper

    return decorator


def cache_invalidate(*patterns: str):
    """
    Decorator to invalidate cache entries after function execution.

    Args:
        *patterns: Cache key patterns to invalidate

    Usage:
        @cache_invalidate("playlist:*")
        def add_tracks_to_playlist(self, playlist_id, track_uris):
            return self.sp.playlist_add_items(playlist_id, track_uris)

    This decorator invalidates matching cache entries after the function
    executes successfully, ensuring stale data is removed.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            cache = get_cache_manager().cache

            # Execute function
            result = func(*args, **kwargs)

            # Invalidate cache patterns on success
            for pattern in patterns:
                cache.clear(pattern)

            return result

        return wrapper

    return decorator


def _generate_cache_key(
    func: Callable,
    prefix: str,
    args: tuple,
    kwargs: dict
) -> str:
    """
    Generate unique cache key from function call.

    Args:
        func: Function being cached
        prefix: Cache key prefix from strategy
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Unique cache key string
    """
    # Build key components
    key_parts = [func.__name__]

    # Add positional args (skip self)
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        elif isinstance(arg, (list, tuple)):
            # For lists/tuples, create hash of sorted items
            try:
                items_str = json.dumps(sorted(arg), default=str)
                key_parts.append(hashlib.md5(items_str.encode()).hexdigest()[:8])
            except (TypeError, ValueError):
                key_parts.append(str(hash(tuple(arg))))

    # Add keyword args (sorted for consistency)
    for key, value in sorted(kwargs.items()):
        if key in ['self', 'cls']:
            continue
        if isinstance(value, (str, int, float, bool, type(None))):
            key_parts.append(f"{key}={value}")
        elif isinstance(value, (list, tuple)):
            try:
                items_str = json.dumps(sorted(value), default=str)
                value_hash = hashlib.md5(items_str.encode()).hexdigest()[:8]
                key_parts.append(f"{key}={value_hash}")
            except (TypeError, ValueError):
                key_parts.append(f"{key}={hash(tuple(value))}")

    # Create final key
    key_string = ":".join(key_parts)

    # If key is too long, hash it
    if len(key_string) > 200:
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}{key_hash}"

    return f"{prefix}{key_string}"


# Convenience decorators for common strategies
def cache_track(func: Callable) -> Callable:
    """Cache track metadata (24h TTL)."""
    return cached(CacheStrategy.TRACK_METADATA)(func)


def cache_album(func: Callable) -> Callable:
    """Cache album metadata (24h TTL)."""
    return cached(CacheStrategy.ALBUM_METADATA)(func)


def cache_artist(func: Callable) -> Callable:
    """Cache artist metadata (24h TTL)."""
    return cached(CacheStrategy.ARTIST_METADATA)(func)


def cache_playlist(func: Callable) -> Callable:
    """Cache playlist metadata (5min TTL)."""
    return cached(CacheStrategy.PLAYLIST_METADATA)(func)


def cache_search(func: Callable) -> Callable:
    """Cache search results (10min TTL)."""
    return cached(CacheStrategy.SEARCH_RESULTS)(func)


def cache_playback(func: Callable) -> Callable:
    """Cache playback state (10s TTL)."""
    return cached(CacheStrategy.PLAYBACK_STATE)(func)
