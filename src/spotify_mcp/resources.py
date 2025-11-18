"""
MCP Resources for Spotify data access.

Resources allow AI to read/query Spotify data without executing tools.
This provides more efficient data access and better caching.
"""

import json
from typing import Any, Dict, List
from datetime import datetime

from spotify_mcp.infrastructure.logging import get_logger
from spotify_mcp.spotify_client import SpotifyClient

logger = get_logger(__name__)


# Resource URI scheme: spotify://category/item
# Examples:
#   - spotify://playback/current - Current playback state
#   - spotify://playlists - User's playlists
#   - spotify://library/recent - Recently played tracks
#   - spotify://user/profile - User profile
#   - spotify://devices - Available playback devices


class SpotifyResources:
    """Handler for Spotify MCP resources."""

    def __init__(self, client: SpotifyClient):
        """
        Initialize Spotify resources handler.

        Args:
            client: Authenticated Spotify client
        """
        self.client = client

    def list_all(self) -> List[Dict[str, Any]]:
        """
        List all available resources.

        Returns:
            List of resource definitions
        """
        return [
            {
                "uri": "spotify://playback/current",
                "name": "Current Playback",
                "description": "Real-time playback state including current track, device, and controls",
                "mimeType": "application/json"
            },
            {
                "uri": "spotify://playlists",
                "name": "User Playlists",
                "description": "All user playlists with metadata",
                "mimeType": "application/json"
            },
            {
                "uri": "spotify://library/recent",
                "name": "Recently Played",
                "description": "Last 50 recently played tracks",
                "mimeType": "application/json"
            },
            {
                "uri": "spotify://user/profile",
                "name": "User Profile",
                "description": "Spotify user profile information",
                "mimeType": "application/json"
            },
            {
                "uri": "spotify://devices",
                "name": "Available Devices",
                "description": "Spotify Connect devices for playback",
                "mimeType": "application/json"
            },
            {
                "uri": "spotify://library/saved-tracks",
                "name": "Saved Tracks",
                "description": "User's saved/liked tracks (first 50)",
                "mimeType": "application/json"
            },
            {
                "uri": "spotify://library/saved-albums",
                "name": "Saved Albums",
                "description": "User's saved albums (first 50)",
                "mimeType": "application/json"
            },
            {
                "uri": "spotify://queue",
                "name": "Playback Queue",
                "description": "Current playback queue",
                "mimeType": "application/json"
            }
        ]

    async def read(self, uri: str) -> Dict[str, Any]:
        """
        Read a resource by URI.

        Args:
            uri: Resource URI (e.g., "spotify://playback/current")

        Returns:
            Resource data as dictionary

        Raises:
            ValueError: If URI is invalid or resource not found
        """
        logger.info(f"Reading resource: {uri}")

        # Parse URI
        if not uri.startswith("spotify://"):
            raise ValueError(f"Invalid resource URI: {uri}. Must start with 'spotify://'")

        path = uri.replace("spotify://", "")
        parts = path.split("/")

        # Route to appropriate handler
        try:
            if path == "playback/current":
                data = await self._get_current_playback()
            elif path == "playlists":
                data = await self._get_playlists()
            elif path == "library/recent":
                data = await self._get_recently_played()
            elif path == "user/profile":
                data = await self._get_user_profile()
            elif path == "devices":
                data = await self._get_devices()
            elif path == "library/saved-tracks":
                data = await self._get_saved_tracks()
            elif path == "library/saved-albums":
                data = await self._get_saved_albums()
            elif path == "queue":
                data = await self._get_queue()
            else:
                raise ValueError(f"Unknown resource: {uri}")

            # Add metadata
            return {
                "uri": uri,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }

        except Exception as e:
            logger.error(f"Failed to read resource {uri}: {e}", exc_info=True)
            raise

    # Resource handlers

    async def _get_current_playback(self) -> Dict[str, Any]:
        """Get current playback state."""
        playback = self.client.current_playback()

        if not playback:
            return {
                "is_playing": False,
                "message": "No active playback"
            }

        # Extract key information
        track = playback.get("item", {})
        device = playback.get("device", {})

        return {
            "is_playing": playback.get("is_playing", False),
            "shuffle_state": playback.get("shuffle_state", False),
            "repeat_state": playback.get("repeat_state", "off"),
            "progress_ms": playback.get("progress_ms", 0),
            "track": {
                "id": track.get("id"),
                "name": track.get("name"),
                "artists": [{"name": a["name"], "id": a["id"]} for a in track.get("artists", [])],
                "album": track.get("album", {}).get("name"),
                "duration_ms": track.get("duration_ms"),
                "uri": track.get("uri")
            } if track else None,
            "device": {
                "id": device.get("id"),
                "name": device.get("name"),
                "type": device.get("type"),
                "volume_percent": device.get("volume_percent")
            } if device else None,
            "context": playback.get("context")
        }

    async def _get_playlists(self) -> Dict[str, Any]:
        """Get user's playlists."""
        playlists_response = self.client.current_user_playlists(limit=50)
        playlists = playlists_response.get("items", [])

        return {
            "total": playlists_response.get("total", 0),
            "playlists": [
                {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "description": p.get("description"),
                    "tracks_total": p.get("tracks", {}).get("total", 0),
                    "owner": p.get("owner", {}).get("display_name"),
                    "public": p.get("public"),
                    "collaborative": p.get("collaborative"),
                    "uri": p.get("uri")
                }
                for p in playlists
            ]
        }

    async def _get_recently_played(self) -> Dict[str, Any]:
        """Get recently played tracks."""
        recent = self.client.current_user_recently_played(limit=50)
        items = recent.get("items", [])

        return {
            "total": len(items),
            "tracks": [
                {
                    "played_at": item.get("played_at"),
                    "track": {
                        "id": item.get("track", {}).get("id"),
                        "name": item.get("track", {}).get("name"),
                        "artists": [a["name"] for a in item.get("track", {}).get("artists", [])],
                        "album": item.get("track", {}).get("album", {}).get("name"),
                        "uri": item.get("track", {}).get("uri")
                    }
                }
                for item in items
            ]
        }

    async def _get_user_profile(self) -> Dict[str, Any]:
        """Get user profile information."""
        user = self.client.current_user()

        return {
            "id": user.get("id"),
            "display_name": user.get("display_name"),
            "email": user.get("email"),
            "country": user.get("country"),
            "product": user.get("product"),
            "followers": user.get("followers", {}).get("total", 0),
            "uri": user.get("uri")
        }

    async def _get_devices(self) -> Dict[str, Any]:
        """Get available playback devices."""
        devices_response = self.client.devices()
        devices = devices_response.get("devices", [])

        return {
            "total": len(devices),
            "devices": [
                {
                    "id": d.get("id"),
                    "name": d.get("name"),
                    "type": d.get("type"),
                    "is_active": d.get("is_active", False),
                    "is_private_session": d.get("is_private_session", False),
                    "is_restricted": d.get("is_restricted", False),
                    "volume_percent": d.get("volume_percent")
                }
                for d in devices
            ]
        }

    async def _get_saved_tracks(self) -> Dict[str, Any]:
        """Get user's saved tracks."""
        saved = self.client.current_user_saved_tracks(limit=50)
        items = saved.get("items", [])

        return {
            "total": saved.get("total", 0),
            "tracks": [
                {
                    "added_at": item.get("added_at"),
                    "track": {
                        "id": item.get("track", {}).get("id"),
                        "name": item.get("track", {}).get("name"),
                        "artists": [a["name"] for a in item.get("track", {}).get("artists", [])],
                        "album": item.get("track", {}).get("album", {}).get("name"),
                        "duration_ms": item.get("track", {}).get("duration_ms"),
                        "uri": item.get("track", {}).get("uri")
                    }
                }
                for item in items
            ]
        }

    async def _get_saved_albums(self) -> Dict[str, Any]:
        """Get user's saved albums."""
        saved = self.client.current_user_saved_albums(limit=50)
        items = saved.get("items", [])

        return {
            "total": saved.get("total", 0),
            "albums": [
                {
                    "added_at": item.get("added_at"),
                    "album": {
                        "id": item.get("album", {}).get("id"),
                        "name": item.get("album", {}).get("name"),
                        "artists": [a["name"] for a in item.get("album", {}).get("artists", [])],
                        "release_date": item.get("album", {}).get("release_date"),
                        "total_tracks": item.get("album", {}).get("total_tracks"),
                        "uri": item.get("album", {}).get("uri")
                    }
                }
                for item in items
            ]
        }

    async def _get_queue(self) -> Dict[str, Any]:
        """Get playback queue."""
        queue = self.client.queue()

        currently_playing = queue.get("currently_playing")
        queue_items = queue.get("queue", [])

        return {
            "currently_playing": {
                "id": currently_playing.get("id"),
                "name": currently_playing.get("name"),
                "artists": [a["name"] for a in currently_playing.get("artists", [])],
                "uri": currently_playing.get("uri")
            } if currently_playing else None,
            "queue_length": len(queue_items),
            "next_tracks": [
                {
                    "id": track.get("id"),
                    "name": track.get("name"),
                    "artists": [a["name"] for a in track.get("artists", [])],
                    "duration_ms": track.get("duration_ms"),
                    "uri": track.get("uri")
                }
                for track in queue_items[:10]  # First 10 tracks
            ]
        }


# Global resources instance
_resources: SpotifyResources = None


def get_resources(client: SpotifyClient) -> SpotifyResources:
    """
    Get or create resources instance.

    Args:
        client: Spotify client

    Returns:
        Resources handler
    """
    global _resources
    if _resources is None or _resources.client != client:
        _resources = SpotifyResources(client)
    return _resources
