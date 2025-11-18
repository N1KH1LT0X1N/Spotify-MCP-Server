"""Cache warming for Spotify MCP Server."""

import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime

from spotify_mcp.infrastructure.logging import get_logger

logger = get_logger(__name__)


class CacheWarmer:
    """
    Pre-populate cache with frequently accessed data.

    Improves cold start performance by pre-loading common data
    that users are likely to request immediately after startup.
    """

    def __init__(self, spotify_client, cache_manager):
        """
        Initialize cache warmer.

        Args:
            spotify_client: Spotify client for fetching data
            cache_manager: CacheManager instance to warm caches
        """
        self.client = spotify_client
        self.cache_manager = cache_manager
        self.warmed_keys: List[str] = []
        self.warming_stats = {
            "last_warming": None,
            "total_warmings": 0,
            "last_duration_seconds": 0,
            "keys_warmed": 0
        }

    async def warm_all(self) -> Dict[str, Any]:
        """
        Warm all critical caches on startup.

        Returns:
            Dictionary with warming statistics
        """
        start_time = datetime.utcnow()
        logger.info("Starting cache warming...")

        try:
            # Run warming tasks concurrently
            results = await asyncio.gather(
                self._warm_user_profile(),
                self._warm_playlists(),
                self._warm_saved_tracks(),
                self._warm_playback_state(),
                self._warm_devices(),
                return_exceptions=True
            )

            # Count successes
            successes = sum(1 for r in results if not isinstance(r, Exception))
            failures = sum(1 for r in results if isinstance(r, Exception))

            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            # Update stats
            self.warming_stats.update({
                "last_warming": end_time.isoformat(),
                "total_warmings": self.warming_stats["total_warmings"] + 1,
                "last_duration_seconds": duration,
                "keys_warmed": len(self.warmed_keys)
            })

            logger.info(
                f"Cache warming completed in {duration:.2f}s",
                extra={
                    "duration_seconds": duration,
                    "successes": successes,
                    "failures": failures,
                    "keys_warmed": len(self.warmed_keys)
                }
            )

            return {
                "status": "completed",
                "duration_seconds": duration,
                "successes": successes,
                "failures": failures,
                "keys_warmed": len(self.warmed_keys),
                "warmed_keys": self.warmed_keys[:10]  # First 10 keys
            }

        except Exception as e:
            logger.error("Cache warming failed", exc_info=True)
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _warm_user_profile(self) -> None:
        """Warm user profile data."""
        try:
            logger.debug("Warming user profile cache...")
            user = await self.client.current_user()

            if user:
                self._mark_warmed("current_user")
                logger.debug("✓ User profile cache warmed")
        except Exception as e:
            logger.warning(f"Failed to warm user profile: {e}")

    async def _warm_playlists(self) -> None:
        """Warm user's playlists cache."""
        try:
            logger.debug("Warming playlists cache...")

            # Fetch first page of playlists (most commonly accessed)
            playlists = await self.client.current_user_playlists(limit=20)

            if playlists:
                self._mark_warmed("user:playlists")
                logger.debug(f"✓ Playlists cache warmed ({len(playlists.get('items', []))} playlists)")

        except Exception as e:
            logger.warning(f"Failed to warm playlists: {e}")

    async def _warm_saved_tracks(self) -> None:
        """Warm user's saved tracks cache."""
        try:
            logger.debug("Warming saved tracks cache...")

            # Fetch first page (most recently saved)
            saved_tracks = await self.client.current_user_saved_tracks(limit=20)

            if saved_tracks:
                self._mark_warmed("saved_tracks")
                logger.debug(f"✓ Saved tracks cache warmed ({len(saved_tracks.get('items', []))} tracks)")

        except Exception as e:
            logger.warning(f"Failed to warm saved tracks: {e}")

    async def _warm_playback_state(self) -> None:
        """Warm current playback state cache."""
        try:
            logger.debug("Warming playback state cache...")

            playback = await self.client.current_playback()

            if playback:
                self._mark_warmed("playback:state")
                logger.debug("✓ Playback state cache warmed")

        except Exception as e:
            logger.warning(f"Failed to warm playback state: {e}")

    async def _warm_devices(self) -> None:
        """Warm available devices cache."""
        try:
            logger.debug("Warming devices cache...")

            devices = await self.client.devices()

            if devices:
                self._mark_warmed("devices")
                logger.debug(f"✓ Devices cache warmed ({len(devices.get('devices', []))} devices)")

        except Exception as e:
            logger.warning(f"Failed to warm devices: {e}")

    def _mark_warmed(self, key: str) -> None:
        """
        Mark a cache key as warmed.

        Args:
            key: Cache key that was warmed
        """
        self.warmed_keys.append(key)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get warming statistics.

        Returns:
            Dictionary with warming stats
        """
        return {
            **self.warming_stats,
            "warmed_keys": self.warmed_keys
        }

    def reset_stats(self) -> None:
        """Reset warming statistics."""
        self.warmed_keys = []
        self.warming_stats = {
            "last_warming": None,
            "total_warmings": 0,
            "last_duration_seconds": 0,
            "keys_warmed": 0
        }


# Global warmer instance
_warmer: Optional[CacheWarmer] = None


def get_cache_warmer():
    """
    Get global cache warmer instance (singleton pattern).

    Returns:
        Global cache warmer
    """
    global _warmer
    return _warmer


def init_warmer(spotify_client, cache_manager) -> CacheWarmer:
    """
    Initialize global cache warmer.

    Args:
        spotify_client: Spotify client instance
        cache_manager: CacheManager instance

    Returns:
        Configured cache warmer
    """
    global _warmer
    _warmer = CacheWarmer(spotify_client, cache_manager)
    return _warmer


async def warm_cache_on_startup(spotify_client, cache_manager) -> Dict[str, Any]:
    """
    Convenience function to warm cache on startup.

    Args:
        spotify_client: Spotify client instance
        cache_manager: CacheManager instance

    Returns:
        Warming statistics
    """
    warmer = init_warmer(spotify_client, cache_manager)
    return await warmer.warm_all()
