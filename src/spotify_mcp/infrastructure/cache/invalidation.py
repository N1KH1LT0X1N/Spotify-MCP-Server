"""Smart cache invalidation for Spotify MCP Server."""

import asyncio
import fnmatch
from typing import List, Optional, Set, Dict, Any
from datetime import datetime

from spotify_mcp.infrastructure.logging import get_logger

logger = get_logger(__name__)


class CacheInvalidator:
    """
    Smart cache invalidation on mutations.

    Automatically invalidates related caches when data changes to prevent
    serving stale data after mutations like adding tracks, creating playlists, etc.
    """

    def __init__(self, cache_manager):
        """
        Initialize cache invalidator.

        Args:
            cache_manager: CacheManager instance to invalidate caches
        """
        self.cache_manager = cache_manager
        self.invalidation_count = 0
        self.invalidation_history: List[Dict[str, Any]] = []

    async def invalidate_playlist(self, playlist_id: str) -> int:
        """
        Invalidate all playlist-related caches.

        When a playlist is modified (tracks added/removed, name changed, etc.),
        invalidate all related cached data.

        Args:
            playlist_id: Spotify playlist ID

        Returns:
            Number of cache entries invalidated
        """
        patterns = [
            f"playlist:{playlist_id}*",  # Direct playlist cache
            f"playlist_tracks:{playlist_id}*",  # Playlist tracks
            "user:playlists:*",  # User's playlist list
            "current_user_playlists:*",  # Paginated playlists
        ]

        count = await self._invalidate_patterns(patterns, "playlist", playlist_id)
        logger.info(
            f"Invalidated {count} playlist cache entries",
            extra={"playlist_id": playlist_id, "patterns": patterns}
        )
        return count

    async def invalidate_library(self, track_id: Optional[str] = None) -> int:
        """
        Invalidate library-related caches.

        When library is modified (tracks saved/removed), invalidate library caches.

        Args:
            track_id: Specific track ID if known (optional)

        Returns:
            Number of cache entries invalidated
        """
        patterns = [
            "saved_tracks:*",  # Saved tracks list
            "user:saved_tracks:*",  # User's saved tracks
        ]

        if track_id:
            patterns.append(f"track:{track_id}:is_saved")

        count = await self._invalidate_patterns(patterns, "library", track_id or "all")
        logger.info(
            f"Invalidated {count} library cache entries",
            extra={"track_id": track_id, "patterns": patterns}
        )
        return count

    async def invalidate_playback(self) -> int:
        """
        Invalidate playback state caches.

        When playback changes (play, pause, skip), invalidate playback caches.

        Returns:
            Number of cache entries invalidated
        """
        patterns = [
            "playback:*",  # Playback state
            "currently_playing:*",  # Currently playing
            "player:*",  # Player state
        ]

        count = await self._invalidate_patterns(patterns, "playback", "state")
        logger.info(
            f"Invalidated {count} playback cache entries",
            extra={"patterns": patterns}
        )
        return count

    async def invalidate_queue(self) -> int:
        """
        Invalidate queue-related caches.

        When queue is modified (tracks added/removed), invalidate queue caches.

        Returns:
            Number of cache entries invalidated
        """
        patterns = [
            "queue:*",  # Queue state
            "user:queue:*",  # User's queue
        ]

        count = await self._invalidate_patterns(patterns, "queue", "state")
        logger.info(
            f"Invalidated {count} queue cache entries",
            extra={"patterns": patterns}
        )
        return count

    async def invalidate_artist(self, artist_id: str) -> int:
        """
        Invalidate artist-related caches.

        When following/unfollowing artists, invalidate artist caches.

        Args:
            artist_id: Spotify artist ID

        Returns:
            Number of cache entries invalidated
        """
        patterns = [
            f"artist:{artist_id}*",  # Artist data
            "following:artists:*",  # Following list
            "user:following:*",  # User's following
        ]

        count = await self._invalidate_patterns(patterns, "artist", artist_id)
        logger.info(
            f"Invalidated {count} artist cache entries",
            extra={"artist_id": artist_id, "patterns": patterns}
        )
        return count

    async def invalidate_album(self, album_id: str) -> int:
        """
        Invalidate album-related caches.

        When album is saved/removed, invalidate album caches.

        Args:
            album_id: Spotify album ID

        Returns:
            Number of cache entries invalidated
        """
        patterns = [
            f"album:{album_id}*",  # Album data
            "saved_albums:*",  # Saved albums
            "user:albums:*",  # User's albums
        ]

        count = await self._invalidate_patterns(patterns, "album", album_id)
        logger.info(
            f"Invalidated {count} album cache entries",
            extra={"album_id": album_id, "patterns": patterns}
        )
        return count

    async def invalidate_devices(self) -> int:
        """
        Invalidate device-related caches.

        When devices change (new device, transfer playback), invalidate device caches.

        Returns:
            Number of cache entries invalidated
        """
        patterns = [
            "devices:*",  # Available devices
            "user:devices:*",  # User's devices
        ]

        count = await self._invalidate_patterns(patterns, "devices", "all")
        logger.info(
            f"Invalidated {count} device cache entries",
            extra={"patterns": patterns}
        )
        return count

    async def invalidate_on_mutation(
        self,
        resource_type: str,
        resource_id: Optional[str] = None,
        operation: Optional[str] = None
    ) -> int:
        """
        Generic invalidation for any mutation.

        Automatically determine what to invalidate based on resource type and operation.

        Args:
            resource_type: Type of resource (playlist, track, artist, etc.)
            resource_id: ID of the resource (optional)
            operation: Operation performed (add, remove, update, etc.)

        Returns:
            Number of cache entries invalidated
        """
        logger.debug(
            f"Invalidating caches for mutation",
            extra={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "operation": operation
            }
        )

        # Route to specific invalidation method
        if resource_type == "playlist":
            return await self.invalidate_playlist(resource_id)
        elif resource_type == "library" or resource_type == "track":
            return await self.invalidate_library(resource_id)
        elif resource_type == "playback":
            return await self.invalidate_playback()
        elif resource_type == "queue":
            return await self.invalidate_queue()
        elif resource_type == "artist":
            return await self.invalidate_artist(resource_id)
        elif resource_type == "album":
            return await self.invalidate_album(resource_id)
        elif resource_type == "devices":
            return await self.invalidate_devices()
        else:
            logger.warning(
                f"Unknown resource type for invalidation: {resource_type}",
                extra={"resource_type": resource_type, "resource_id": resource_id}
            )
            return 0

    async def _invalidate_patterns(
        self,
        patterns: List[str],
        resource_type: str,
        resource_id: str
    ) -> int:
        """
        Invalidate cache entries matching multiple patterns.

        Args:
            patterns: List of cache key patterns to match
            resource_type: Type of resource being invalidated
            resource_id: ID of resource being invalidated

        Returns:
            Total number of cache entries invalidated
        """
        total_count = 0

        for pattern in patterns:
            try:
                # Use cache manager's clear method with pattern
                self.cache_manager.clear(pattern)
                total_count += 1  # Increment for each pattern (actual count may vary)
            except Exception as e:
                logger.error(
                    f"Failed to invalidate pattern: {pattern}",
                    exc_info=True,
                    extra={"pattern": pattern, "error": str(e)}
                )

        # Track invalidation
        self.invalidation_count += total_count
        self.invalidation_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "resource_type": resource_type,
            "resource_id": resource_id,
            "patterns": patterns,
            "count": total_count
        })

        # Keep history manageable (last 100 invalidations)
        if len(self.invalidation_history) > 100:
            self.invalidation_history = self.invalidation_history[-100:]

        return total_count

    def get_stats(self) -> Dict[str, Any]:
        """
        Get invalidation statistics.

        Returns:
            Dictionary with invalidation stats
        """
        return {
            "total_invalidations": self.invalidation_count,
            "recent_invalidations": self.invalidation_history[-10:],  # Last 10
            "history_size": len(self.invalidation_history)
        }

    def reset_stats(self) -> None:
        """Reset invalidation statistics."""
        self.invalidation_count = 0
        self.invalidation_history = []


# Global invalidator instance
_invalidator: Optional[CacheInvalidator] = None


def get_cache_invalidator():
    """
    Get global cache invalidator instance (singleton pattern).

    Returns:
        Global cache invalidator
    """
    global _invalidator
    if _invalidator is None:
        from .manager import get_cache_manager
        _invalidator = CacheInvalidator(get_cache_manager())
    return _invalidator


def init_invalidator(cache_manager) -> CacheInvalidator:
    """
    Initialize global cache invalidator with specific cache manager.

    Args:
        cache_manager: CacheManager instance

    Returns:
        Configured cache invalidator
    """
    global _invalidator
    _invalidator = CacheInvalidator(cache_manager)
    return _invalidator
