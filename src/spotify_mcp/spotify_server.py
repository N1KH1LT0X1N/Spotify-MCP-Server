"""
Spotify MCP Server v3.0 - Enhanced FastMCP Implementation

Complete migration with:
- Structured output using Pydantic models
- Progress reporting for long operations
- Comprehensive tool annotations
- All 75 tools migrated
- Dynamic resource templates
- Completion handlers

Run with: python -m spotify_mcp.spotify_server
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

# Environment setup
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv(usecwd=True)
if not dotenv_path:
    project_root = Path(__file__).parent.parent.parent
    potential_env = project_root / ".env"
    if potential_env.exists():
        dotenv_path = str(potential_env)

has_tokens = os.getenv("SPOTIFY_ACCESS_TOKEN") and os.getenv("SPOTIFY_REFRESH_TOKEN")
if dotenv_path and not has_tokens:
    load_dotenv(dotenv_path)
elif not dotenv_path and not has_tokens:
    load_dotenv()

# FastMCP imports
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import ToolAnnotations

# Spotify imports
from spotify_mcp.auth import get_spotify_client
from spotify_mcp.spotify_client import SpotifyClient

# Import all Pydantic models
from spotify_mcp.models import (
    # Playback
    PlaybackState, PlaybackAction, VolumeAction, ShuffleAction,
    RepeatAction, SeekAction, DeviceList, TransferAction,
    # Track/Artist/Album
    Track, Artist, Album, Device, PlaybackContext,
    # Search
    SearchResult,
    # Library
    SavedTrack, SavedTrackList, LibraryAction, SavedTrackCheckResult,
    # Playlists
    PlaylistBase, PlaylistList, PlaylistCreated, PlaylistAction,
    # Queue
    QueueAction,
    # User
    UserProfile, RecentlyPlayed,
    # Albums
    SavedAlbum
)


# ============================================================================
# Application Context
# ============================================================================

@dataclass
class AppContext:
    """Application context with typed dependencies."""
    spotify_client: SpotifyClient


# Global client reference for resources (set during lifespan)
_global_spotify_client: Optional[SpotifyClient] = None


def get_client() -> SpotifyClient:
    """Get the global Spotify client for resources."""
    if _global_spotify_client is None:
        raise RuntimeError("Spotify client not initialized")
    return _global_spotify_client


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage Spotify client lifecycle."""
    global _global_spotify_client
    
    # Startup
    try:
        if not os.getenv("SPOTIFY_ACCESS_TOKEN") or not os.getenv("SPOTIFY_REFRESH_TOKEN"):
            print("ERROR: No Spotify tokens found.", file=sys.stderr)
            print("Please run: python -m spotify_mcp.auth", file=sys.stderr)
            raise RuntimeError("Spotify authentication required")
        
        sp = get_spotify_client()
        spotify_client = SpotifyClient(sp)
        _global_spotify_client = spotify_client  # Set global reference
        
        print("✓ Spotify MCP Server v3.0 Enhanced initialized", file=sys.stderr)
        
        yield AppContext(spotify_client=spotify_client)
    finally:
        # Shutdown
        _global_spotify_client = None  # Clear global reference
        print("✓ Spotify MCP Server shutdown complete", file=sys.stderr)


# ============================================================================
# Initialize FastMCP Server
# ============================================================================

mcp = FastMCP("spotify-mcp", lifespan=app_lifespan)


# ============================================================================
# PLAYBACK TOOLS - With Structured Output
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Play Music",
    readOnlyHint=False,
    idempotentHint=False,
    destructiveHint=False,
    openWorldHint=True
))
async def play(
    ctx,  # Context[AppContext] - FastMCP injects this
    context_uri: Optional[str] = None,
    uris: Optional[List[str]] = None,
    device_id: Optional[str] = None
) -> dict:
    """Start or resume playback.
    
    Args:
        ctx: FastMCP context for logging and client access
        context_uri: Spotify URI of album, artist, or playlist
        uris: List of track URIs to play
        device_id: Device ID to play on
    
    Returns:
        PlaybackAction with success status
    """
    client = ctx.request_context.lifespan_context.spotify_client
    await ctx.info(f"Starting playback")
    
    client.start_playback(
        device_id=device_id,
        context_uri=context_uri,
        uris=uris,
        offset=None
    )
    
    return {
        "success": True,
        "message": "Playback started",
        "device_id": device_id
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Pause Playback",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def pause(ctx: Context, device_id: Optional[str] = None) -> dict:
    """Pause playback."""
    client = ctx.request_context.lifespan_context.spotify_client
    client.pause_playback(device_id=device_id)
    
    return {
        "success": True,
        "message": "Playback paused",
        "device_id": device_id
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Skip to Next Track",
    readOnlyHint=False,
    idempotentHint=False,
    destructiveHint=False,
    openWorldHint=True
))
async def skip_next(ctx: Context, device_id: Optional[str] = None) -> dict:
    """Skip to next track."""
    client = ctx.request_context.lifespan_context.spotify_client
    client.next_track(device_id=device_id)
    
    return {
        "success": True,
        "message": "Skipped to next track",
        "device_id": device_id
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Skip to Previous Track",
    readOnlyHint=False,
    idempotentHint=False,
    destructiveHint=False,
    openWorldHint=True
))
async def skip_previous(ctx: Context, device_id: Optional[str] = None) -> dict:
    """Skip to previous track."""
    client = ctx.request_context.lifespan_context.spotify_client
    client.previous_track(device_id=device_id)
    
    return {
        "success": True,
        "message": "Skipped to previous track",
        "device_id": device_id
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Current Playback",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_current_playback(ctx) -> dict:
    """Get current playback state with progress reporting."""
    client = ctx.request_context.lifespan_context.spotify_client
    await ctx.debug("Fetching current playback state")
    
    playback = client.current_playback()
    
    if not playback:
        return {
            "is_playing": False,
            "message": "No active playback"
        }
    
    track = playback.get("item", {})
    device = playback.get("device", {})
    context = playback.get("context", {})
    
    return {
        "is_playing": playback.get("is_playing", False),
        "shuffle_state": playback.get("shuffle_state", False),
        "repeat_state": playback.get("repeat_state", "off"),
        "progress_ms": playback.get("progress_ms", 0),
        "track": {
            "id": track.get("id"),
            "name": track.get("name"),
            "uri": track.get("uri"),
            "duration_ms": track.get("duration_ms"),
            "explicit": track.get("explicit", False),
            "popularity": track.get("popularity"),
            "artists": [
                {
                    "id": a.get("id"),
                    "name": a.get("name"),
                    "uri": a.get("uri")
                }
                for a in track.get("artists", [])
            ],
            "album": {
                "id": track.get("album", {}).get("id"),
                "name": track.get("album", {}).get("name"),
                "uri": track.get("album", {}).get("uri"),
                "release_date": track.get("album", {}).get("release_date"),
                "total_tracks": track.get("album", {}).get("total_tracks")
            } if track.get("album") else None
        } if track else None,
        "device": {
            "id": device.get("id"),
            "name": device.get("name"),
            "type": device.get("type"),
            "is_active": device.get("is_active", False),
            "volume_percent": device.get("volume_percent")
        } if device else None,
        "context": {
            "type": context.get("type"),
            "uri": context.get("uri")
        } if context else None
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Available Devices",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_available_devices(ctx) -> dict:
    """Get available playback devices."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    devices_response = client.devices()
    devices = devices_response.get("devices", [])
    
    return {
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
        ],
        "total_devices": len(devices)
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Set Volume",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def set_volume(ctx: Context, volume_percent: int, device_id: Optional[str] = None) -> dict:
    """Set playback volume (0-100)."""
    if not 0 <= volume_percent <= 100:
        raise ValueError("Volume must be between 0 and 100")
    
    client = ctx.request_context.lifespan_context.spotify_client
    client.volume(volume_percent=volume_percent, device_id=device_id)
    
    return {
        "success": True,
        "message": f"Volume set to {volume_percent}%",
        "volume_percent": volume_percent,
        "device_id": device_id
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Set Shuffle Mode",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def set_shuffle(ctx: Context, state: bool, device_id: Optional[str] = None) -> dict:
    """Toggle shuffle mode."""
    client = ctx.request_context.lifespan_context.spotify_client
    client.shuffle(state=state, device_id=device_id)
    
    return {
        "success": True,
        "message": f"Shuffle {'enabled' if state else 'disabled'}",
        "shuffle_state": state,
        "device_id": device_id
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Set Repeat Mode",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def set_repeat(ctx: Context, state: str, device_id: Optional[str] = None) -> dict:
    """Set repeat mode: off, track, context."""
    if state not in ["off", "track", "context"]:
        raise ValueError("Repeat state must be: off, track, or context")
    
    client = ctx.request_context.lifespan_context.spotify_client
    client.repeat(state=state, device_id=device_id)
    
    return {
        "success": True,
        "message": f"Repeat set to {state}",
        "repeat_state": state,
        "device_id": device_id
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Seek to Position",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def seek_to_position(ctx: Context, position_ms: int, device_id: Optional[str] = None) -> dict:
    """Seek to position in current track."""
    if position_ms < 0:
        raise ValueError("Position must be non-negative")
    
    client = ctx.request_context.lifespan_context.spotify_client
    client.seek_track(position_ms=position_ms, device_id=device_id)
    
    return {
        "success": True,
        "message": f"Seeked to {position_ms}ms",
        "position_ms": position_ms,
        "device_id": device_id
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Transfer Playback",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def transfer_playback(ctx: Context, device_id: str, ensure_playback: bool = False) -> dict:
    """Transfer playback to another device."""
    client = ctx.request_context.lifespan_context.spotify_client
    client.transfer_playback(device_id=device_id, force_play=ensure_playback)
    
    return {
        "success": True,
        "message": f"Playback transferred to device {device_id}",
        "device_id": device_id,
        "ensure_playback": ensure_playback
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Recently Played",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_recently_played(ctx: Context, limit: int = 20) -> dict:
    """Get recently played tracks."""
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")
    
    client = ctx.request_context.lifespan_context.spotify_client
    result = client.current_user_recently_played(limit=limit)
    
    items = result.get("items", [])
    
    return {
        "items": [
            {
                "played_at": item.get("played_at"),
                "track": {
                    "id": item.get("track", {}).get("id"),
                    "name": item.get("track", {}).get("name"),
                    "uri": item.get("track", {}).get("uri"),
                    "duration_ms": item.get("track", {}).get("duration_ms"),
                    "artists": [
                        {"id": a.get("id"), "name": a.get("name"), "uri": a.get("uri")}
                        for a in item.get("track", {}).get("artists", [])
                    ]
                }
            }
            for item in items
        ],
        "total": len(items),
        "cursors": result.get("cursors")
    }


# ============================================================================
# SEARCH TOOLS
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Search Spotify",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def search(
    ctx,
    query: str,
    search_type: str = "track",
    limit: int = 20,
    offset: int = 0
) -> dict:
    """Search for tracks, albums, artists, or playlists.
    
    Args:
        ctx: FastMCP context
        query: Search query string
        search_type: Type to search for (track, album, artist, playlist)
        limit: Number of results (1-50)
        offset: Offset for pagination
    """
    client = ctx.request_context.lifespan_context.spotify_client
    
    valid_types = ["track", "album", "artist", "playlist"]
    if search_type not in valid_types:
        raise ValueError(f"search_type must be one of: {', '.join(valid_types)}")
    
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")
    
    results = client.search(q=query, limit=limit, offset=offset, type=search_type)
    
    key = f"{search_type}s"
    items = results.get(key, {}).get("items", [])
    total = results.get(key, {}).get("total", 0)
    
    return {
        "query": query,
        "type": search_type,
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": items
    }


# ============================================================================
# LIBRARY TOOLS
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Get Saved Tracks",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def get_saved_tracks(ctx: Context, limit: int = 20, offset: int = 0) -> dict:
    """Get user's saved tracks from library."""
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")
    
    client = ctx.request_context.lifespan_context.spotify_client
    result = client.current_user_saved_tracks(limit=limit, offset=offset)
    
    items = result.get("items", [])
    
    return {
        "items": [
            {
                "added_at": item.get("added_at"),
                "track": item.get("track")
            }
            for item in items
        ],
        "total": result.get("total", 0),
        "limit": limit,
        "offset": offset
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Save Tracks to Library",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def save_tracks(ctx: Context, track_ids: List[str]) -> dict:
    """Save tracks to library."""
    if not track_ids:
        raise ValueError("Must provide at least one track ID")
    
    if len(track_ids) > 50:
        raise ValueError("Cannot save more than 50 tracks at once")
    
    client = ctx.request_context.lifespan_context.spotify_client
    
    # Progress reporting for bulk operations
    # In a real implementation with Context, we would use:
    # await ctx.report_progress(0, len(track_ids), "Saving tracks...")
    
    client.current_user_saved_tracks_add(tracks=track_ids)
    
    return {
        "success": True,
        "message": f"Saved {len(track_ids)} tracks",
        "track_count": len(track_ids),
        "track_ids": track_ids
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Remove Saved Tracks",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=True,
    openWorldHint=False
))
async def remove_saved_tracks(ctx: Context, track_ids: List[str]) -> dict:
    """Remove tracks from library."""
    if not track_ids:
        raise ValueError("Must provide at least one track ID")
    
    if len(track_ids) > 50:
        raise ValueError("Cannot remove more than 50 tracks at once")
    
    client = ctx.request_context.lifespan_context.spotify_client
    client.current_user_saved_tracks_delete(tracks=track_ids)
    
    return {
        "success": True,
        "message": f"Removed {len(track_ids)} tracks",
        "track_count": len(track_ids),
        "track_ids": track_ids
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Check Saved Tracks",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def check_saved_tracks(ctx: Context, track_ids: List[str]) -> dict:
    """Check if tracks are in library."""
    if not track_ids:
        raise ValueError("Must provide at least one track ID")
    
    if len(track_ids) > 50:
        raise ValueError("Cannot check more than 50 tracks at once")
    
    client = ctx.request_context.lifespan_context.spotify_client
    results = client.current_user_saved_tracks_contains(tracks=track_ids)
    
    return {
        "track_ids": track_ids,
        "saved_status": [
            {"track_id": track_id, "is_saved": is_saved}
            for track_id, is_saved in zip(track_ids, results)
        ],
        "total_saved": sum(results)
    }


# ============================================================================
# QUEUE TOOLS
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Get Queue",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_queue(ctx) -> dict:
    """Get the user's playback queue."""
    client = ctx.request_context.lifespan_context.spotify_client
    queue = client.queue()
    
    return {
        "currently_playing": queue.get("currently_playing"),
        "queue": queue.get("queue", []),
        "queue_length": len(queue.get("queue", []))
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Add to Queue",
    readOnlyHint=False,
    idempotentHint=False,
    destructiveHint=False,
    openWorldHint=True
))
async def add_to_queue(ctx: Context, uri: str, device_id: Optional[str] = None) -> dict:
    """Add a track to the queue."""
    client = ctx.request_context.lifespan_context.spotify_client
    client.add_to_queue(uri=uri, device_id=device_id)
    
    return {
        "success": True,
        "message": "Track added to queue",
        "uri": uri,
        "device_id": device_id
    }


# ============================================================================
# USER TOOLS
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Get Current User Profile",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def get_current_user(ctx) -> dict:
    """Get current user's profile."""
    client = ctx.request_context.lifespan_context.spotify_client
    user = client.current_user()
    
    return {
        "id": user.get("id"),
        "display_name": user.get("display_name"),
        "email": user.get("email"),
        "country": user.get("country"),
        "product": user.get("product"),
        "followers": user.get("followers", {}).get("total"),
        "uri": user.get("uri"),
        "images": user.get("images", [])
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Top Tracks",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def get_top_tracks(ctx: Context, limit: int = 20, time_range: str = "medium_term") -> dict:
    """Get user's top tracks."""
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")
    
    valid_ranges = ["short_term", "medium_term", "long_term"]
    if time_range not in valid_ranges:
        raise ValueError(f"time_range must be one of: {', '.join(valid_ranges)}")
    
    client = ctx.request_context.lifespan_context.spotify_client
    result = client.current_user_top_tracks(limit=limit, time_range=time_range)
    
    return {
        "items": result.get("items", []),
        "total": result.get("total", 0),
        "limit": limit,
        "time_range": time_range
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Top Artists",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def get_top_artists(ctx: Context, limit: int = 20, time_range: str = "medium_term") -> dict:
    """Get user's top artists."""
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")
    
    valid_ranges = ["short_term", "medium_term", "long_term"]
    if time_range not in valid_ranges:
        raise ValueError(f"time_range must be one of: {', '.join(valid_ranges)}")
    
    client = ctx.request_context.lifespan_context.spotify_client
    result = client.current_user_top_artists(limit=limit, time_range=time_range)
    
    return {
        "items": result.get("items", []),
        "total": result.get("total", 0),
        "limit": limit,
        "time_range": time_range
    }


# ============================================================================
# PLAYLIST TOOLS - With Progress Reporting
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Get User Playlists",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def get_user_playlists(ctx: Context, limit: int = 20, offset: int = 0) -> dict:
    """Get current user's playlists."""
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")
    
    client = ctx.request_context.lifespan_context.spotify_client
    result = client.current_user_playlists(limit=limit, offset=offset)
    
    return {
        "items": result.get("items", []),
        "total": result.get("total", 0),
        "limit": limit,
        "offset": offset
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Create Playlist",
    readOnlyHint=False,
    idempotentHint=False,
    destructiveHint=False,
    openWorldHint=False
))
async def create_playlist(
    ctx,
    name: str,
    description: Optional[str] = None,
    public: bool = True
) -> dict:
    """Create a new playlist."""
    client = ctx.request_context.lifespan_context.spotify_client
    user = client.current_user()
    
    playlist = client.user_playlist_create(
        user=user["id"],
        name=name,
        public=public,
        description=description or ""
    )
    
    return {
        "success": True,
        "message": f"Created playlist: {name}",
        "playlist": {
            "id": playlist.get("id"),
            "name": playlist.get("name"),
            "uri": playlist.get("uri"),
            "public": playlist.get("public"),
            "description": playlist.get("description"),
            "tracks_total": playlist.get("tracks", {}).get("total", 0)
        }
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Add Tracks to Playlist",
    readOnlyHint=False,
    idempotentHint=False,
    destructiveHint=False,
    openWorldHint=False
))
async def add_tracks_to_playlist(ctx: Context, playlist_id: str, track_uris: List[str]) -> dict:
    """Add tracks to a playlist with progress reporting."""
    if not track_uris:
        raise ValueError("Must provide at least one track URI")
    
    client = ctx.request_context.lifespan_context.spotify_client
    
    # Progress reporting for bulk operations
    await ctx.report_progress(0, len(track_uris), "Adding tracks...")
    
    # Spotify allows 100 tracks per request
    batch_size = 100
    added_count = 0
    
    for i in range(0, len(track_uris), batch_size):
        batch = track_uris[i:i + batch_size]
        client.playlist_add_items(playlist_id=playlist_id, items=batch)
        added_count += len(batch)
        
        await ctx.report_progress(added_count, len(track_uris), f"Added {added_count}/{len(track_uris)} tracks")
    
    return {
        "success": True,
        "message": f"Added {len(track_uris)} tracks to playlist",
        "playlist_id": playlist_id,
        "tracks_added": len(track_uris)
    }


# ============================================================================
# ALBUM TOOLS
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Get Album Details",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_album(ctx: Context, album_id: str) -> dict:
    """Get detailed information about an album including tracks, artists, and metadata."""
    client = ctx.request_context.lifespan_context.spotify_client
    await ctx.debug(f"Fetching album: {album_id}")
    
    # Extract ID from URI if needed
    album_id = album_id.split(":")[-1] if ":" in album_id else album_id
    
    album = client.album(album_id)
    
    return {
        "id": album["id"],
        "uri": album["uri"],
        "name": album["name"],
        "artists": [
            {"name": a["name"], "uri": a["uri"], "id": a["id"]}
            for a in album.get("artists", [])
        ],
        "release_date": album.get("release_date"),
        "total_tracks": album.get("total_tracks", 0),
        "album_type": album.get("album_type"),
        "label": album.get("label"),
        "popularity": album.get("popularity", 0),
        "genres": album.get("genres", []),
        "images": album.get("images", []),
        "external_urls": album.get("external_urls", {}),
        "tracks": [
            {
                "name": track["name"],
                "uri": track["uri"],
                "id": track["id"],
                "track_number": track["track_number"],
                "duration_ms": track["duration_ms"],
                "explicit": track.get("explicit", False),
                "artists": [
                    {"name": a["name"], "uri": a["uri"]}
                    for a in track.get("artists", [])
                ]
            }
            for track in album.get("tracks", {}).get("items", [])
        ]
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Album Tracks",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_album_tracks(ctx: Context, album_id: str, limit: int = 50, offset: int = 0) -> dict:
    """Get tracks from an album with pagination."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    album_id = album_id.split(":")[-1] if ":" in album_id else album_id
    
    results = client.album_tracks(album_id, limit=limit, offset=offset)
    items = results.get("items", [])
    total = results.get("total", 0)
    
    return {
        "tracks": [
            {
                "name": track["name"],
                "uri": track["uri"],
                "id": track["id"],
                "track_number": track["track_number"],
                "duration_ms": track["duration_ms"],
                "explicit": track.get("explicit", False),
                "artists": [
                    {"name": a["name"], "uri": a["uri"], "id": a["id"]}
                    for a in track.get("artists", [])
                ]
            }
            for track in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Saved Albums",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def get_saved_albums(ctx: Context, limit: int = 20, offset: int = 0) -> dict:
    """Get user's saved (liked) albums from library."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    results = client.current_user_saved_albums(limit=limit, offset=offset)
    items = results.get("items", [])
    total = results.get("total", 0)
    
    return {
        "albums": [
            {
                "added_at": item.get("added_at"),
                "album": {
                    "id": item["album"]["id"],
                    "uri": item["album"]["uri"],
                    "name": item["album"]["name"],
                    "artists": [
                        {"name": a["name"], "uri": a["uri"], "id": a["id"]}
                        for a in item["album"].get("artists", [])
                    ],
                    "release_date": item["album"].get("release_date"),
                    "total_tracks": item["album"].get("total_tracks", 0),
                    "album_type": item["album"].get("album_type"),
                    "images": item["album"].get("images", [])
                }
            }
            for item in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Save Albums to Library",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def save_albums(ctx: Context, album_ids: List[str]) -> dict:
    """Save (like) albums to user's library."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not album_ids:
        raise ValueError("album_ids cannot be empty")
    if len(album_ids) > 50:
        raise ValueError("Cannot save more than 50 albums at once")
    
    album_ids = [a.split(":")[-1] if ":" in a else a for a in album_ids]
    client.current_user_saved_albums_add(albums=album_ids)
    
    return {
        "success": True,
        "message": f"Saved {len(album_ids)} album(s)",
        "album_count": len(album_ids),
        "album_ids": album_ids
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Remove Saved Albums",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=True,
    openWorldHint=False
))
async def remove_saved_albums(ctx: Context, album_ids: List[str]) -> dict:
    """Remove albums from user's library."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not album_ids:
        raise ValueError("album_ids cannot be empty")
    if len(album_ids) > 50:
        raise ValueError("Cannot remove more than 50 albums at once")
    
    album_ids = [a.split(":")[-1] if ":" in a else a for a in album_ids]
    client.current_user_saved_albums_delete(albums=album_ids)
    
    return {
        "success": True,
        "message": f"Removed {len(album_ids)} album(s)",
        "album_count": len(album_ids),
        "album_ids": album_ids
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Check Saved Albums",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def check_saved_albums(ctx: Context, album_ids: List[str]) -> dict:
    """Check if albums are saved in user's library."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not album_ids:
        raise ValueError("album_ids cannot be empty")
    if len(album_ids) > 20:
        raise ValueError("Cannot check more than 20 albums at once")
    
    album_ids = [a.split(":")[-1] if ":" in a else a for a in album_ids]
    results = client.current_user_saved_albums_contains(albums=album_ids)
    
    return {
        "albums": [
            {"album_id": album_id, "is_saved": is_saved}
            for album_id, is_saved in zip(album_ids, results)
        ],
        "total_checked": len(album_ids),
        "total_saved": sum(results)
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get New Releases",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_new_releases(ctx: Context, limit: int = 20, offset: int = 0, country: Optional[str] = None) -> dict:
    """Get new album releases featured on Spotify."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    results = client.new_releases(limit=limit, offset=offset, country=country)
    albums = results.get("albums", {})
    items = albums.get("items", [])
    total = albums.get("total", 0)
    
    return {
        "albums": [
            {
                "id": album["id"],
                "uri": album["uri"],
                "name": album["name"],
                "artists": [
                    {"name": a["name"], "uri": a["uri"], "id": a["id"]}
                    for a in album.get("artists", [])
                ],
                "release_date": album.get("release_date"),
                "total_tracks": album.get("total_tracks", 0),
                "album_type": album.get("album_type"),
                "images": album.get("images", [])
            }
            for album in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


# ============================================================================
# ARTIST TOOLS
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Get Artist Details",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_artist(ctx: Context, artist_id: str) -> dict:
    """Get detailed information about an artist including genres, popularity, and followers."""
    client = ctx.request_context.lifespan_context.spotify_client
    await ctx.debug(f"Fetching artist: {artist_id}")
    
    artist_id = artist_id.split(":")[-1] if ":" in artist_id else artist_id
    artist = client.artist(artist_id)
    
    return {
        "id": artist["id"],
        "uri": artist["uri"],
        "name": artist["name"],
        "genres": artist.get("genres", []),
        "popularity": artist.get("popularity", 0),
        "followers": artist.get("followers", {}).get("total", 0),
        "images": artist.get("images", []),
        "external_urls": artist.get("external_urls", {}),
        "type": artist["type"]
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Artist Albums",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_artist_albums(
    ctx,
    artist_id: str,
    include_groups: Optional[List[str]] = None,
    limit: int = 20,
    offset: int = 0
) -> dict:
    """Get an artist's albums, singles, compilations, and appearances."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    artist_id = artist_id.split(":")[-1] if ":" in artist_id else artist_id
    
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    valid_groups = ["album", "single", "appears_on", "compilation"]
    if include_groups:
        invalid = [g for g in include_groups if g not in valid_groups]
        if invalid:
            raise ValueError(f"Invalid include_groups: {invalid}")
        include_groups_str = ",".join(include_groups)
    else:
        include_groups_str = None
    
    results = client.artist_albums(
        artist_id,
        album_type=include_groups_str,
        limit=limit,
        offset=offset
    )
    
    items = results.get("items", [])
    total = results.get("total", 0)
    
    return {
        "artist_id": artist_id,
        "albums": [
            {
                "id": album["id"],
                "uri": album["uri"],
                "name": album["name"],
                "album_type": album.get("album_type"),
                "release_date": album.get("release_date"),
                "total_tracks": album.get("total_tracks", 0),
                "images": album.get("images", []),
                "artists": [
                    {"name": a["name"], "uri": a["uri"], "id": a["id"]}
                    for a in album.get("artists", [])
                ]
            }
            for album in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Artist Top Tracks",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_artist_top_tracks(ctx: Context, artist_id: str, market: str = "US") -> dict:
    """Get an artist's top 10 tracks in a specific market."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    artist_id = artist_id.split(":")[-1] if ":" in artist_id else artist_id
    results = client.artist_top_tracks(artist_id, country=market)
    tracks = results.get("tracks", [])
    
    return {
        "artist_id": artist_id,
        "market": market,
        "tracks": [
            {
                "id": track["id"],
                "uri": track["uri"],
                "name": track["name"],
                "popularity": track.get("popularity", 0),
                "duration_ms": track.get("duration_ms"),
                "explicit": track.get("explicit", False),
                "album": {
                    "name": track.get("album", {}).get("name"),
                    "uri": track.get("album", {}).get("uri"),
                    "id": track.get("album", {}).get("id"),
                    "release_date": track.get("album", {}).get("release_date")
                },
                "artists": [
                    {"name": a["name"], "uri": a["uri"], "id": a["id"]}
                    for a in track.get("artists", [])
                ],
                "preview_url": track.get("preview_url")
            }
            for track in tracks
        ],
        "total": len(tracks)
    }


# ============================================================================
# TRACK TOOLS
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Get Track Details",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_track(ctx: Context, track_id: str, market: Optional[str] = None) -> dict:
    """Get detailed information about a track."""
    client = ctx.request_context.lifespan_context.spotify_client
    await ctx.debug(f"Fetching track: {track_id}")
    
    track_id = track_id.split(":")[-1] if ":" in track_id else track_id
    result = client.track(track_id, market)
    
    return {
        "success": True,
        "track": {
            "id": result.get("id"),
            "uri": result.get("uri"),
            "name": result.get("name"),
            "artists": [
                {"name": a["name"], "id": a["id"], "uri": a["uri"]}
                for a in result.get("artists", [])
            ],
            "album": {
                "name": result.get("album", {}).get("name"),
                "id": result.get("album", {}).get("id"),
                "uri": result.get("album", {}).get("uri"),
                "release_date": result.get("album", {}).get("release_date")
            },
            "duration_ms": result.get("duration_ms"),
            "explicit": result.get("explicit", False),
            "popularity": result.get("popularity", 0),
            "track_number": result.get("track_number"),
            "disc_number": result.get("disc_number", 1),
            "external_urls": result.get("external_urls", {}),
            "preview_url": result.get("preview_url")
        }
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Multiple Tracks",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_several_tracks(ctx: Context, track_ids: List[str], market: Optional[str] = None) -> dict:
    """Get detailed information about multiple tracks (up to 50)."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not track_ids:
        raise ValueError("track_ids cannot be empty")
    if len(track_ids) > 50:
        raise ValueError("Cannot retrieve more than 50 tracks at once")
    
    track_ids = [t.split(":")[-1] if ":" in t else t for t in track_ids]
    result = client.tracks(track_ids, market)
    
    tracks = []
    for track in result.get("tracks", []):
        if track:
            tracks.append({
                "id": track.get("id"),
                "uri": track.get("uri"),
                "name": track.get("name"),
                "artists": [
                    {"name": a["name"], "id": a["id"]}
                    for a in track.get("artists", [])
                ],
                "album": {
                    "name": track.get("album", {}).get("name"),
                    "id": track.get("album", {}).get("id")
                },
                "duration_ms": track.get("duration_ms"),
                "explicit": track.get("explicit", False),
                "popularity": track.get("popularity", 0)
            })
    
    return {
        "success": True,
        "tracks": tracks,
        "total": len(tracks)
    }


# ============================================================================
# ADDITIONAL PLAYLIST TOOLS
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Get Playlist Details",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_playlist(
    ctx,
    playlist_id: str,
    include_tracks: bool = True,
    tracks_limit: int = 100,
    tracks_offset: int = 0
) -> dict:
    """Get detailed information about a playlist with optional track listing."""
    client = ctx.request_context.lifespan_context.spotify_client
    await ctx.debug(f"Fetching playlist: {playlist_id}")
    
    playlist_id = playlist_id.split(":")[-1] if ":" in playlist_id else playlist_id
    
    if not 1 <= tracks_limit <= 100:
        raise ValueError("tracks_limit must be between 1 and 100")
    
    playlist = client.playlist(playlist_id=playlist_id)
    
    result = {
        "name": playlist["name"],
        "uri": playlist["uri"],
        "id": playlist["id"],
        "description": playlist.get("description"),
        "owner": {
            "display_name": playlist.get("owner", {}).get("display_name"),
            "id": playlist.get("owner", {}).get("id")
        },
        "total_tracks": playlist.get("tracks", {}).get("total", 0),
        "public": playlist.get("public", False),
        "collaborative": playlist.get("collaborative", False),
        "snapshot_id": playlist.get("snapshot_id"),
        "followers": playlist.get("followers", {}).get("total", 0)
    }
    
    if include_tracks:
        tracks_result = client.playlist_items(
            playlist_id=playlist_id,
            limit=tracks_limit,
            offset=tracks_offset
        )
        
        items = tracks_result.get("items", [])
        
        result["tracks"] = {
            "items": [
                {
                    "added_at": item.get("added_at"),
                    "track": {
                        "name": item["track"]["name"],
                        "uri": item["track"]["uri"],
                        "id": item["track"]["id"],
                        "artists": [
                            {"name": a["name"], "uri": a["uri"]} 
                            for a in item["track"].get("artists", [])
                        ],
                        "album": {
                            "name": item["track"].get("album", {}).get("name"),
                            "uri": item["track"].get("album", {}).get("uri"),
                        },
                        "duration_ms": item["track"].get("duration_ms"),
                        "explicit": item["track"].get("explicit", False),
                        "popularity": item["track"].get("popularity", 0)
                    } if item.get("track") else None
                }
                for item in items
                if item.get("track")
            ],
            "total": tracks_result.get("total", 0),
            "limit": tracks_limit,
            "offset": tracks_offset,
            "has_more": tracks_offset + tracks_limit < tracks_result.get("total", 0)
        }
    
    return result


@mcp.tool(annotations=ToolAnnotations(
    title="Get Playlist Tracks",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_playlist_tracks(ctx: Context, playlist_id: str, limit: int = 100, offset: int = 0) -> dict:
    """Get tracks from a playlist with pagination."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    playlist_id = playlist_id.split(":")[-1] if ":" in playlist_id else playlist_id
    
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    
    await ctx.report_progress(0, 100, "Fetching playlist tracks...")
    
    results = client.playlist_items(
        playlist_id=playlist_id,
        limit=limit,
        offset=offset
    )
    
    items = results.get("items", [])
    total = results.get("total", 0)
    
    await ctx.report_progress(100, 100, f"Retrieved {len(items)} tracks")
    
    return {
        "tracks": [
            {
                "added_at": item.get("added_at"),
                "track": {
                    "name": item["track"]["name"],
                    "uri": item["track"]["uri"],
                    "id": item["track"]["id"],
                    "artists": [
                        {"name": a["name"], "uri": a["uri"]}
                        for a in item["track"].get("artists", [])
                    ],
                    "album": {
                        "name": item["track"].get("album", {}).get("name"),
                        "uri": item["track"].get("album", {}).get("uri")
                    },
                    "duration_ms": item["track"].get("duration_ms")
                } if item.get("track") else None
            }
            for item in items
            if item.get("track")
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Update Playlist Details",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def update_playlist_details(
    ctx,
    playlist_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    public: Optional[bool] = None
) -> dict:
    """Update a playlist's name, description, or public status."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    playlist_id = playlist_id.split(":")[-1] if ":" in playlist_id else playlist_id
    
    if name is None and description is None and public is None:
        raise ValueError("At least one of name, description, or public must be provided")
    
    await ctx.info(f"Updating playlist {playlist_id}")
    
    client.playlist_change_details(
        playlist_id=playlist_id,
        name=name,
        description=description,
        public=public
    )
    
    return {
        "success": True,
        "message": "Playlist updated successfully",
        "playlist_id": playlist_id,
        "updated_fields": {
            "name": name,
            "description": description,
            "public": public
        }
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Remove Tracks from Playlist",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=True,
    openWorldHint=False
))
async def remove_tracks_from_playlist(ctx: Context, playlist_id: str, track_uris: List[str]) -> dict:
    """Remove tracks from a playlist."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    playlist_id = playlist_id.split(":")[-1] if ":" in playlist_id else playlist_id
    
    if not track_uris:
        raise ValueError("track_uris cannot be empty")
    
    await ctx.info(f"Removing {len(track_uris)} tracks from playlist")
    
    tracks = [{"uri": uri} for uri in track_uris]
    client.playlist_remove_all_occurrences_of_items(
        playlist_id=playlist_id,
        items=tracks
    )
    
    return {
        "success": True,
        "message": f"Removed {len(track_uris)} track(s) from playlist",
        "playlist_id": playlist_id,
        "tracks_removed": len(track_uris)
    }


# ============================================================================
# SHOW/PODCAST TOOLS
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Get Show Details",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_show(ctx: Context, show_id: str, market: Optional[str] = None) -> dict:
    """Get detailed information about a podcast show."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    show_id = show_id.split(":")[-1] if ":" in show_id else show_id
    result = client.show(show_id, market)
    
    return {
        "success": True,
        "show": {
            "id": result.get("id"),
            "uri": result.get("uri"),
            "name": result.get("name"),
            "description": result.get("description"),
            "publisher": result.get("publisher"),
            "media_type": result.get("media_type"),
            "total_episodes": result.get("total_episodes", 0),
            "languages": result.get("languages", []),
            "explicit": result.get("explicit", False),
            "images": result.get("images", []),
            "external_urls": result.get("external_urls", {})
        }
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Show Episodes",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_show_episodes(
    ctx,
    show_id: str,
    limit: int = 20,
    offset: int = 0,
    market: Optional[str] = None
) -> dict:
    """Get episodes from a podcast show with pagination."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    show_id = show_id.split(":")[-1] if ":" in show_id else show_id
    result = client.show_episodes(show_id, limit=limit, offset=offset, market=market)
    
    items = result.get("items", [])
    total = result.get("total", 0)
    
    return {
        "success": True,
        "episodes": [
            {
                "id": ep.get("id"),
                "uri": ep.get("uri"),
                "name": ep.get("name"),
                "description": ep.get("description"),
                "release_date": ep.get("release_date"),
                "duration_ms": ep.get("duration_ms"),
                "explicit": ep.get("explicit", False),
                "languages": ep.get("languages", []),
                "images": ep.get("images", [])
            }
            for ep in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Saved Shows",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def get_saved_shows(ctx: Context, limit: int = 20, offset: int = 0) -> dict:
    """Get user's saved podcast shows."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    result = client.current_user_saved_shows(limit=limit, offset=offset)
    items = result.get("items", [])
    total = result.get("total", 0)
    
    return {
        "shows": [
            {
                "added_at": item.get("added_at"),
                "show": {
                    "id": item["show"]["id"],
                    "uri": item["show"]["uri"],
                    "name": item["show"]["name"],
                    "publisher": item["show"].get("publisher"),
                    "total_episodes": item["show"].get("total_episodes", 0),
                    "images": item["show"].get("images", [])
                }
            }
            for item in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Save Shows to Library",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def save_shows(ctx: Context, show_ids: List[str]) -> dict:
    """Save podcast shows to user's library."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not show_ids:
        raise ValueError("show_ids cannot be empty")
    if len(show_ids) > 50:
        raise ValueError("Cannot save more than 50 shows at once")
    
    show_ids = [s.split(":")[-1] if ":" in s else s for s in show_ids]
    client.current_user_saved_shows_add(shows=show_ids)
    
    return {
        "success": True,
        "message": f"Saved {len(show_ids)} show(s)",
        "show_count": len(show_ids)
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Remove Saved Shows",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=True,
    openWorldHint=False
))
async def remove_saved_shows(ctx: Context, show_ids: List[str]) -> dict:
    """Remove podcast shows from user's library."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not show_ids:
        raise ValueError("show_ids cannot be empty")
    if len(show_ids) > 50:
        raise ValueError("Cannot remove more than 50 shows at once")
    
    show_ids = [s.split(":")[-1] if ":" in s else s for s in show_ids]
    client.current_user_saved_shows_delete(shows=show_ids)
    
    return {
        "success": True,
        "message": f"Removed {len(show_ids)} show(s)",
        "show_count": len(show_ids)
    }


# ============================================================================
# EPISODE TOOLS
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Get Episode Details",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_episode(ctx: Context, episode_id: str, market: Optional[str] = None) -> dict:
    """Get detailed information about a podcast episode."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    episode_id = episode_id.split(":")[-1] if ":" in episode_id else episode_id
    result = client.episode(episode_id, market)
    
    return {
        "id": result.get("id"),
        "name": result.get("name"),
        "description": result.get("description"),
        "duration_ms": result.get("duration_ms"),
        "explicit": result.get("explicit"),
        "release_date": result.get("release_date"),
        "resume_point": result.get("resume_point"),
        "show": {
            "id": result.get("show", {}).get("id"),
            "name": result.get("show", {}).get("name"),
            "publisher": result.get("show", {}).get("publisher")
        },
        "audio_preview_url": result.get("audio_preview_url"),
        "images": result.get("images", []),
        "languages": result.get("languages", []),
        "is_playable": result.get("is_playable")
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Saved Episodes",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def get_saved_episodes(ctx: Context, limit: int = 20, offset: int = 0, market: Optional[str] = None) -> dict:
    """Get user's saved podcast episodes."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    result = client.current_user_saved_episodes(limit=limit, offset=offset, market=market)
    
    episodes = []
    for item in result.get("items", []):
        episode = item.get("episode", {})
        episodes.append({
            "id": episode.get("id"),
            "name": episode.get("name"),
            "description": episode.get("description"),
            "duration_ms": episode.get("duration_ms"),
            "release_date": episode.get("release_date"),
            "show": {
                "id": episode.get("show", {}).get("id"),
                "name": episode.get("show", {}).get("name")
            },
            "added_at": item.get("added_at")
        })
    
    return {
        "episodes": episodes,
        "total": result.get("total", 0),
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < result.get("total", 0)
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Save Episodes to Library",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def save_episodes(ctx: Context, episode_ids: List[str]) -> dict:
    """Save podcast episodes to user's library."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not episode_ids:
        raise ValueError("episode_ids cannot be empty")
    if len(episode_ids) > 50:
        raise ValueError("Cannot save more than 50 episodes at once")
    
    episode_ids = [e.split(":")[-1] if ":" in e else e for e in episode_ids]
    client.current_user_saved_episodes_add(episodes=episode_ids)
    
    return {
        "success": True,
        "message": f"Saved {len(episode_ids)} episode(s)",
        "episode_count": len(episode_ids)
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Remove Saved Episodes",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=True,
    openWorldHint=False
))
async def remove_saved_episodes(ctx: Context, episode_ids: List[str]) -> dict:
    """Remove podcast episodes from user's library."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not episode_ids:
        raise ValueError("episode_ids cannot be empty")
    if len(episode_ids) > 50:
        raise ValueError("Cannot remove more than 50 episodes at once")
    
    episode_ids = [e.split(":")[-1] if ":" in e else e for e in episode_ids]
    client.current_user_saved_episodes_delete(episodes=episode_ids)
    
    return {
        "success": True,
        "message": f"Removed {len(episode_ids)} episode(s)",
        "episode_count": len(episode_ids)
    }


# ============================================================================
# COMPOSITE TOOLS (Multi-Step Operations with Progress Reporting)
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Create Playlist with Tracks",
    readOnlyHint=False,
    idempotentHint=False,
    destructiveHint=False,
    openWorldHint=False
))
async def create_playlist_with_tracks(
    ctx,
    name: str,
    track_uris: List[str],
    public: bool = True,
    description: str = ""
) -> dict:
    """Create a new playlist and add tracks in one operation with progress reporting."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not track_uris:
        raise ValueError("track_uris cannot be empty")
    
    total_steps = 2 + (len(track_uris) // 100) + 1
    
    await ctx.report_progress(0, total_steps, "Creating playlist...")
    
    # Step 1: Create playlist
    user = client.current_user()
    playlist = client.user_playlist_create(
        user=user["id"],
        name=name,
        public=public,
        description=description
    )
    playlist_id = playlist["id"]
    
    await ctx.report_progress(1, total_steps, "Adding tracks...")
    
    # Step 2: Add tracks in batches
    added_count = 0
    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i + 100]
        client.playlist_add_items(playlist_id, batch)
        added_count += len(batch)
        await ctx.report_progress(
            2 + (i // 100),
            total_steps,
            f"Added {added_count}/{len(track_uris)} tracks"
        )
    
    await ctx.report_progress(total_steps, total_steps, "Complete!")
    
    return {
        "success": True,
        "message": f"Created playlist '{name}' with {len(track_uris)} tracks",
        "playlist": {
            "id": playlist["id"],
            "uri": playlist["uri"],
            "name": playlist["name"]
        },
        "tracks_added": len(track_uris)
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Artist Full Profile",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_artist_full_profile(ctx: Context, artist_id: str) -> dict:
    """Get comprehensive artist info including top tracks and albums."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    artist_id = artist_id.split(":")[-1] if ":" in artist_id else artist_id
    
    await ctx.report_progress(0, 3, "Fetching artist info...")
    artist = client.artist(artist_id)
    
    await ctx.report_progress(1, 3, "Fetching top tracks...")
    top_tracks = client.artist_top_tracks(artist_id)
    
    await ctx.report_progress(2, 3, "Fetching albums...")
    albums = client.artist_albums(artist_id, limit=20)
    
    await ctx.report_progress(3, 3, "Complete!")
    
    return {
        "artist": {
            "id": artist["id"],
            "uri": artist["uri"],
            "name": artist["name"],
            "genres": artist.get("genres", []),
            "popularity": artist.get("popularity", 0),
            "followers": artist.get("followers", {}).get("total", 0),
            "images": artist.get("images", [])
        },
        "top_tracks": [
            {
                "id": t["id"],
                "uri": t["uri"],
                "name": t["name"],
                "popularity": t.get("popularity", 0)
            }
            for t in top_tracks.get("tracks", [])[:10]
        ],
        "albums": [
            {
                "id": a["id"],
                "uri": a["uri"],
                "name": a["name"],
                "album_type": a.get("album_type"),
                "release_date": a.get("release_date")
            }
            for a in albums.get("items", [])
        ],
        "total_albums": albums.get("total", 0)
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Search and Play",
    readOnlyHint=False,
    idempotentHint=False,
    destructiveHint=False,
    openWorldHint=True
))
async def search_and_play(
    ctx,
    query: str,
    search_type: str = "track",
    device_id: Optional[str] = None
) -> dict:
    """Search for music and immediately start playing the first result."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    await ctx.report_progress(0, 2, f"Searching for {search_type}...")
    
    results = client.search(q=query, limit=1, type=search_type)
    key = f"{search_type}s"
    items = results.get(key, {}).get("items", [])
    
    if not items:
        return {
            "success": False,
            "message": f"No {search_type} found for query: {query}"
        }
    
    await ctx.report_progress(1, 2, "Starting playback...")
    
    item = items[0]
    uri = item["uri"]
    
    if search_type == "track":
        client.start_playback(device_id=device_id, uris=[uri])
    else:
        client.start_playback(device_id=device_id, context_uri=uri)
    
    await ctx.report_progress(2, 2, "Playing!")
    
    return {
        "success": True,
        "message": f"Now playing: {item['name']}",
        "item": {
            "id": item["id"],
            "uri": item["uri"],
            "name": item["name"],
            "type": search_type
        }
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Listening Summary",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def get_listening_summary(ctx: Context, time_range: str = "medium_term") -> dict:
    """Get a summary of user's listening history with top tracks, artists, and genres."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    valid_ranges = ["short_term", "medium_term", "long_term"]
    if time_range not in valid_ranges:
        raise ValueError(f"time_range must be one of: {', '.join(valid_ranges)}")
    
    await ctx.report_progress(0, 4, "Fetching top tracks...")
    top_tracks = client.current_user_top_tracks(limit=20, time_range=time_range)
    
    await ctx.report_progress(1, 4, "Fetching top artists...")
    top_artists = client.current_user_top_artists(limit=20, time_range=time_range)
    
    await ctx.report_progress(2, 4, "Fetching recently played...")
    recent = client.current_user_recently_played(limit=20)
    
    await ctx.report_progress(3, 4, "Analyzing genres...")
    
    # Aggregate genres from top artists
    genre_counts = {}
    for artist in top_artists.get("items", []):
        for genre in artist.get("genres", []):
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    await ctx.report_progress(4, 4, "Complete!")
    
    return {
        "time_range": time_range,
        "time_range_description": {
            "short_term": "Last 4 weeks",
            "medium_term": "Last 6 months",
            "long_term": "All time"
        }.get(time_range),
        "top_tracks": [
            {
                "name": t["name"],
                "artist": t["artists"][0]["name"] if t.get("artists") else "Unknown",
                "popularity": t.get("popularity", 0)
            }
            for t in top_tracks.get("items", [])[:10]
        ],
        "top_artists": [
            {
                "name": a["name"],
                "genres": a.get("genres", [])[:3],
                "popularity": a.get("popularity", 0)
            }
            for a in top_artists.get("items", [])[:10]
        ],
        "top_genres": [{"genre": g, "count": c} for g, c in top_genres],
        "recently_played_count": len(recent.get("items", []))
    }


# ============================================================================
# CATEGORIES TOOLS
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Get Browse Categories",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_categories(
    ctx,
    country: Optional[str] = None,
    locale: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> dict:
    """
    Get a list of Spotify browse categories for content discovery.
    
    Args:
        country: ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB')
        locale: Desired language for category names (e.g., 'en_US', 'es_MX')
        limit: Maximum number of categories to return (1-50)
        offset: Index of first category to return for pagination
    """
    client = ctx.request_context.lifespan_context.spotify_client
    await ctx.debug(f"Fetching browse categories (country={country}, locale={locale})")
    
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    result = client.categories(country=country, locale=locale, limit=limit, offset=offset)
    
    categories = []
    for cat in result.get("categories", {}).get("items", []):
        categories.append({
            "id": cat.get("id"),
            "name": cat.get("name"),
            "href": cat.get("href"),
            "icons": [
                {
                    "url": icon.get("url"),
                    "width": icon.get("width"),
                    "height": icon.get("height")
                }
                for icon in cat.get("icons", [])
            ]
        })
    
    total = result.get("categories", {}).get("total", 0)
    
    return {
        "success": True,
        "categories": categories,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Category Details",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_category(
    ctx,
    category_id: str,
    country: Optional[str] = None,
    locale: Optional[str] = None
) -> dict:
    """
    Get detailed information about a specific Spotify browse category.
    
    Args:
        category_id: The Spotify category ID (e.g., 'toplists', 'hiphop', 'rock')
        country: ISO 3166-1 alpha-2 country code
        locale: Desired language for category name
    """
    client = ctx.request_context.lifespan_context.spotify_client
    await ctx.debug(f"Fetching category: {category_id}")
    
    if not category_id:
        raise ValueError("category_id is required")
    
    result = client.category(category_id, country=country, locale=locale)
    
    return {
        "success": True,
        "category": {
            "id": result.get("id"),
            "name": result.get("name"),
            "href": result.get("href"),
            "icons": [
                {
                    "url": icon.get("url"),
                    "width": icon.get("width"),
                    "height": icon.get("height")
                }
                for icon in result.get("icons", [])
            ]
        }
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Category Playlists",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_category_playlists(
    ctx,
    category_id: str,
    country: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> dict:
    """
    Get playlists for a specific Spotify browse category.
    
    Args:
        category_id: The Spotify category ID (e.g., 'toplists', 'hiphop', 'rock')
        country: ISO 3166-1 alpha-2 country code
        limit: Maximum number of playlists to return (1-50)
        offset: Index of first playlist to return for pagination
    """
    client = ctx.request_context.lifespan_context.spotify_client
    await ctx.debug(f"Fetching playlists for category: {category_id}")
    
    if not category_id:
        raise ValueError("category_id is required")
    
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    result = client.category_playlists(category_id, country=country, limit=limit, offset=offset)
    
    playlists = []
    for pl in result.get("playlists", {}).get("items", []):
        if pl:
            playlists.append({
                "id": pl.get("id"),
                "uri": pl.get("uri"),
                "name": pl.get("name"),
                "description": pl.get("description"),
                "owner": {
                    "display_name": pl.get("owner", {}).get("display_name"),
                    "id": pl.get("owner", {}).get("id")
                },
                "total_tracks": pl.get("tracks", {}).get("total", 0),
                "images": [
                    {"url": img.get("url"), "width": img.get("width"), "height": img.get("height")}
                    for img in pl.get("images", [])[:1]  # Just first image
                ]
            })
    
    total = result.get("playlists", {}).get("total", 0)
    
    return {
        "success": True,
        "category_id": category_id,
        "playlists": playlists,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


# ============================================================================
# MARKETS TOOLS
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Get Available Markets",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_available_markets(ctx) -> dict:
    """
    Get the list of markets (countries) where Spotify is available.
    
    Returns ISO 3166-1 alpha-2 country codes for all markets where
    Spotify is currently available. Use these codes when specifying
    markets in other API calls.
    """
    client = ctx.request_context.lifespan_context.spotify_client
    await ctx.debug("Fetching available markets")
    
    result = client.available_markets()
    
    markets = result.get("markets", [])
    
    return {
        "success": True,
        "markets": sorted(markets),  # Sort alphabetically
        "total": len(markets),
        "usage": "Use these ISO 3166-1 alpha-2 country codes (e.g., 'US', 'GB', 'DE') when specifying markets in other API calls"
    }


# ============================================================================
# ADDITIONAL BATCH/SEVERAL TOOLS
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Get Multiple Albums",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_several_albums(
    ctx,
    album_ids: List[str],
    market: Optional[str] = None
) -> dict:
    """Get multiple albums by their IDs (up to 20 at once)."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not album_ids:
        raise ValueError("album_ids cannot be empty")
    if len(album_ids) > 20:
        raise ValueError("Cannot retrieve more than 20 albums at once")
    
    album_ids = [a.split(":")[-1] if ":" in a else a for a in album_ids]
    result = client.albums(album_ids)
    
    albums = []
    for album in result.get("albums", []):
        if album:
            albums.append({
                "id": album.get("id"),
                "uri": album.get("uri"),
                "name": album.get("name"),
                "artists": [{"name": a["name"], "id": a["id"]} for a in album.get("artists", [])],
                "release_date": album.get("release_date"),
                "total_tracks": album.get("total_tracks"),
                "album_type": album.get("album_type")
            })
    
    return {"success": True, "albums": albums, "total": len(albums)}


@mcp.tool(annotations=ToolAnnotations(
    title="Get Multiple Artists",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_several_artists(
    ctx,
    artist_ids: List[str]
) -> dict:
    """Get multiple artists by their IDs (up to 50 at once)."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not artist_ids:
        raise ValueError("artist_ids cannot be empty")
    if len(artist_ids) > 50:
        raise ValueError("Cannot retrieve more than 50 artists at once")
    
    artist_ids = [a.split(":")[-1] if ":" in a else a for a in artist_ids]
    result = client.artists(artist_ids)
    
    artists = []
    for artist in result.get("artists", []):
        if artist:
            artists.append({
                "id": artist.get("id"),
                "uri": artist.get("uri"),
                "name": artist.get("name"),
                "genres": artist.get("genres", []),
                "popularity": artist.get("popularity", 0),
                "followers": artist.get("followers", {}).get("total", 0)
            })
    
    return {"success": True, "artists": artists, "total": len(artists)}


@mcp.tool(annotations=ToolAnnotations(
    title="Get Multiple Shows",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_several_shows(
    ctx,
    show_ids: List[str],
    market: Optional[str] = None
) -> dict:
    """Get multiple shows/podcasts by their IDs (up to 50 at once)."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not show_ids:
        raise ValueError("show_ids cannot be empty")
    if len(show_ids) > 50:
        raise ValueError("Cannot retrieve more than 50 shows at once")
    
    show_ids = [s.split(":")[-1] if ":" in s else s for s in show_ids]
    result = client.shows(show_ids, market=market)
    
    shows = []
    for show in result.get("shows", []):
        if show:
            shows.append({
                "id": show.get("id"),
                "uri": show.get("uri"),
                "name": show.get("name"),
                "publisher": show.get("publisher"),
                "description": show.get("description", "")[:200],
                "total_episodes": show.get("total_episodes", 0)
            })
    
    return {"success": True, "shows": shows, "total": len(shows)}


@mcp.tool(annotations=ToolAnnotations(
    title="Get Multiple Episodes",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_several_episodes(
    ctx,
    episode_ids: List[str],
    market: Optional[str] = None
) -> dict:
    """Get multiple podcast episodes by their IDs (up to 50 at once)."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not episode_ids:
        raise ValueError("episode_ids cannot be empty")
    if len(episode_ids) > 50:
        raise ValueError("Cannot retrieve more than 50 episodes at once")
    
    episode_ids = [e.split(":")[-1] if ":" in e else e for e in episode_ids]
    result = client.episodes(episode_ids, market=market)
    
    episodes = []
    for ep in result.get("episodes", []):
        if ep:
            episodes.append({
                "id": ep.get("id"),
                "uri": ep.get("uri"),
                "name": ep.get("name"),
                "description": ep.get("description", "")[:200],
                "duration_ms": ep.get("duration_ms"),
                "release_date": ep.get("release_date"),
                "show": {"name": ep.get("show", {}).get("name"), "id": ep.get("show", {}).get("id")}
            })
    
    return {"success": True, "episodes": episodes, "total": len(episodes)}


@mcp.tool(annotations=ToolAnnotations(
    title="Check Saved Shows",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def check_saved_shows(ctx: Context, show_ids: List[str]) -> dict:
    """Check if shows are saved in user's library."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not show_ids:
        raise ValueError("show_ids cannot be empty")
    if len(show_ids) > 50:
        raise ValueError("Cannot check more than 50 shows at once")
    
    show_ids = [s.split(":")[-1] if ":" in s else s for s in show_ids]
    results = client.current_user_saved_shows_contains(show_ids)
    
    return {
        "success": True,
        "results": [{"id": sid, "is_saved": saved} for sid, saved in zip(show_ids, results)],
        "total_saved": sum(results)
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Check Saved Episodes",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def check_saved_episodes(ctx: Context, episode_ids: List[str]) -> dict:
    """Check if episodes are saved in user's library."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not episode_ids:
        raise ValueError("episode_ids cannot be empty")
    if len(episode_ids) > 50:
        raise ValueError("Cannot check more than 50 episodes at once")
    
    episode_ids = [e.split(":")[-1] if ":" in e else e for e in episode_ids]
    results = client.current_user_saved_episodes_contains(episode_ids)
    
    return {
        "success": True,
        "results": [{"id": eid, "is_saved": saved} for eid, saved in zip(episode_ids, results)],
        "total_saved": sum(results)
    }


# ============================================================================
# USER & FOLLOW TOOLS
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Get User Profile",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_user_profile(ctx: Context, user_id: str) -> dict:
    """Get a user's public profile information."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    user_id = user_id.split(":")[-1] if ":" in user_id else user_id
    user = client.user(user_id)
    
    return {
        "success": True,
        "user": {
            "id": user.get("id"),
            "display_name": user.get("display_name"),
            "uri": user.get("uri"),
            "followers": user.get("followers", {}).get("total", 0),
            "external_urls": user.get("external_urls", {}),
            "images": user.get("images", [])
        }
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Top Items",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def get_top_items(
    ctx,
    item_type: str = "tracks",
    time_range: str = "medium_term",
    limit: int = 20,
    offset: int = 0
) -> dict:
    """
    Get the user's top tracks or artists.
    
    Args:
        item_type: Type of items - "tracks" or "artists"
        time_range: "short_term" (4 weeks), "medium_term" (6 months), "long_term" (years)
        limit: Maximum number of items (1-50)
        offset: Offset for pagination
    """
    client = ctx.request_context.lifespan_context.spotify_client
    
    valid_types = ["tracks", "artists"]
    if item_type not in valid_types:
        raise ValueError(f"item_type must be one of: {', '.join(valid_types)}")
    
    valid_ranges = ["short_term", "medium_term", "long_term"]
    if time_range not in valid_ranges:
        raise ValueError(f"time_range must be one of: {', '.join(valid_ranges)}")
    
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    if item_type == "tracks":
        results = client.current_user_top_tracks(limit=limit, offset=offset, time_range=time_range)
        items = [
            {
                "name": item["name"], "uri": item["uri"], "id": item["id"],
                "artists": [{"name": a["name"], "uri": a["uri"]} for a in item.get("artists", [])],
                "popularity": item.get("popularity", 0)
            }
            for item in results.get("items", [])
        ]
    else:
        results = client.current_user_top_artists(limit=limit, offset=offset, time_range=time_range)
        items = [
            {
                "name": item["name"], "uri": item["uri"], "id": item["id"],
                "genres": item.get("genres", []), "popularity": item.get("popularity", 0),
                "followers": item.get("followers", {}).get("total", 0)
            }
            for item in results.get("items", [])
        ]
    
    time_range_descriptions = {"short_term": "last 4 weeks", "medium_term": "last 6 months", "long_term": "all time"}
    
    return {
        "type": item_type, "time_range": time_range,
        "time_range_description": time_range_descriptions[time_range],
        "items": items, "total": results.get("total", 0),
        "limit": limit, "offset": offset, "has_more": offset + limit < results.get("total", 0)
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Get Followed Artists",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def get_followed_artists(ctx: Context, limit: int = 20, after: Optional[str] = None) -> dict:
    """Get artists followed by the current user."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    result = client.current_user_following_artists(limit=limit, after=after)
    artists = result.get("artists", {})
    
    return {
        "success": True,
        "artists": [
            {
                "id": a.get("id"), "uri": a.get("uri"), "name": a.get("name"),
                "genres": a.get("genres", []), "popularity": a.get("popularity", 0),
                "followers": a.get("followers", {}).get("total", 0)
            }
            for a in artists.get("items", [])
        ],
        "total": artists.get("total", 0),
        "cursors": artists.get("cursors", {})
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Follow Artists or Users",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def follow_artists_or_users(ctx: Context, ids: List[str], follow_type: str = "artist") -> dict:
    """Follow one or more artists or users."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not ids:
        raise ValueError("ids cannot be empty")
    if len(ids) > 50:
        raise ValueError("Cannot follow more than 50 at once")
    
    valid_types = ["artist", "user"]
    if follow_type not in valid_types:
        raise ValueError(f"follow_type must be one of: {', '.join(valid_types)}")
    
    ids = [id.split(":")[-1] if ":" in id else id for id in ids]
    
    if follow_type == "artist":
        client.user_follow_artists(ids=ids)
    else:
        client.user_follow_users(ids=ids)
    
    return {"success": True, "message": f"Successfully followed {len(ids)} {follow_type}(s)", "count": len(ids)}


@mcp.tool(annotations=ToolAnnotations(
    title="Unfollow Artists or Users",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=True,
    openWorldHint=False
))
async def unfollow_artists_or_users(ctx: Context, ids: List[str], follow_type: str = "artist") -> dict:
    """Unfollow one or more artists or users."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not ids:
        raise ValueError("ids cannot be empty")
    if len(ids) > 50:
        raise ValueError("Cannot unfollow more than 50 at once")
    
    valid_types = ["artist", "user"]
    if follow_type not in valid_types:
        raise ValueError(f"follow_type must be one of: {', '.join(valid_types)}")
    
    ids = [id.split(":")[-1] if ":" in id else id for id in ids]
    
    if follow_type == "artist":
        client.user_unfollow_artists(ids=ids)
    else:
        client.user_unfollow_users(ids=ids)
    
    return {"success": True, "message": f"Successfully unfollowed {len(ids)} {follow_type}(s)", "count": len(ids)}


@mcp.tool(annotations=ToolAnnotations(
    title="Check Following Status",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def check_following_artists_or_users(ctx: Context, ids: List[str], follow_type: str = "artist") -> dict:
    """Check if current user follows artists or users."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    if not ids:
        raise ValueError("ids cannot be empty")
    if len(ids) > 50:
        raise ValueError("Cannot check more than 50 at once")
    
    valid_types = ["artist", "user"]
    if follow_type not in valid_types:
        raise ValueError(f"follow_type must be one of: {', '.join(valid_types)}")
    
    ids = [id.split(":")[-1] if ":" in id else id for id in ids]
    results = client.current_user_following_contains(ids=ids, follow_type=follow_type)
    
    return {
        "success": True, "type": follow_type,
        "following": [{"id": id, "is_following": is_following} for id, is_following in zip(ids, results)],
        "total_following": sum(results)
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Check Playlist Follow Status",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def check_current_user_follows_playlist(ctx: Context, playlist_id: str, user_ids: Optional[List[str]] = None) -> dict:
    """Check if current user (or specified users) follow a playlist."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    playlist_id = playlist_id.split(":")[-1] if ":" in playlist_id else playlist_id
    
    if not user_ids:
        current = client.current_user()
        user_ids = [current.get("id")]
    else:
        user_ids = [id.split(":")[-1] if ":" in id else id for id in user_ids]
    
    if len(user_ids) > 5:
        raise ValueError("Cannot check more than 5 users at once")
    
    results = client.playlist_is_following(playlist_id=playlist_id, user_ids=user_ids)
    
    return {
        "success": True, "playlist_id": playlist_id,
        "users": [{"user_id": uid, "is_following": following} for uid, following in zip(user_ids, results)]
    }


# ============================================================================
# ADDITIONAL PLAYLIST MANAGEMENT TOOLS
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Change Playlist Details",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def change_playlist_details(
    ctx,
    playlist_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    public: Optional[bool] = None,
    collaborative: Optional[bool] = None
) -> dict:
    """Change playlist details (name, description, public/private, collaborative)."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    playlist_id = playlist_id.split(":")[-1] if ":" in playlist_id else playlist_id
    
    if not any([name, description, public is not None, collaborative is not None]):
        raise ValueError("At least one field must be provided to update")
    
    client.playlist_change_details(
        playlist_id=playlist_id, name=name, description=description, public=public, collaborative=collaborative
    )
    
    return {
        "success": True, "message": "Playlist details updated",
        "updated_fields": {k: v for k, v in {"name": name, "description": description, "public": public, "collaborative": collaborative}.items() if v is not None}
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Reorder Playlist Items",
    readOnlyHint=False,
    idempotentHint=False,
    destructiveHint=False,
    openWorldHint=False
))
async def update_playlist_items(
    ctx,
    playlist_id: str,
    range_start: int,
    insert_before: int,
    range_length: int = 1
) -> dict:
    """Reorder items in a playlist (move tracks to different positions)."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    playlist_id = playlist_id.split(":")[-1] if ":" in playlist_id else playlist_id
    
    if range_start < 0:
        raise ValueError("range_start must be >= 0")
    if insert_before < 0:
        raise ValueError("insert_before must be >= 0")
    if range_length < 1:
        raise ValueError("range_length must be >= 1")
    
    result = client.playlist_reorder_items(
        playlist_id=playlist_id, range_start=range_start, insert_before=insert_before, range_length=range_length
    )
    
    return {"success": True, "message": f"Reordered {range_length} item(s)", "snapshot_id": result.get("snapshot_id")}


@mcp.tool(annotations=ToolAnnotations(
    title="Get Playlist Cover Image",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_playlist_cover_image(ctx: Context, playlist_id: str) -> dict:
    """Get the cover image for a playlist."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    playlist_id = playlist_id.split(":")[-1] if ":" in playlist_id else playlist_id
    images = client.playlist_cover_image(playlist_id=playlist_id)
    
    return {
        "playlist_id": playlist_id,
        "images": [{"url": img.get("url"), "height": img.get("height"), "width": img.get("width")} for img in images]
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Add Custom Playlist Cover",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def add_custom_playlist_cover_image(ctx: Context, playlist_id: str, image_base64: str) -> dict:
    """Add a custom cover image to a playlist. Image must be base64 encoded JPEG, max 256KB."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    playlist_id = playlist_id.split(":")[-1] if ":" in playlist_id else playlist_id
    
    if not image_base64:
        raise ValueError("image_base64 cannot be empty")
    
    client.playlist_upload_cover_image(playlist_id=playlist_id, image_b64=image_base64)
    
    return {"success": True, "message": "Custom cover image uploaded", "playlist_id": playlist_id}


@mcp.tool(annotations=ToolAnnotations(
    title="Get User Playlists by ID",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def get_user_playlists_by_id(ctx: Context, user_id: str, limit: int = 50, offset: int = 0) -> dict:
    """Get playlists owned by a specific user."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    user_id = user_id.split(":")[-1] if ":" in user_id else user_id
    
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    results = client.user_playlists(user=user_id, limit=limit, offset=offset)
    
    return {
        "success": True,
        "playlists": [
            {
                "name": p["name"], "uri": p["uri"], "id": p["id"],
                "owner": {"display_name": p.get("owner", {}).get("display_name"), "id": p.get("owner", {}).get("id")},
                "total_tracks": p.get("tracks", {}).get("total", 0), "public": p.get("public", False)
            }
            for p in results.get("items", [])
        ],
        "total": results.get("total", 0), "limit": limit, "offset": offset,
        "has_more": offset + limit < results.get("total", 0)
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Follow Playlist",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def follow_playlist(ctx: Context, playlist_id: str, public: bool = True) -> dict:
    """Follow a playlist."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    playlist_id = playlist_id.split(":")[-1] if ":" in playlist_id else playlist_id
    client.current_user_follow_playlist(playlist_id=playlist_id, public=public)
    
    return {"success": True, "message": "Successfully followed playlist", "playlist_id": playlist_id}


@mcp.tool(annotations=ToolAnnotations(
    title="Unfollow Playlist",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=True,
    openWorldHint=False
))
async def unfollow_playlist(ctx: Context, playlist_id: str) -> dict:
    """Unfollow a playlist."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    playlist_id = playlist_id.split(":")[-1] if ":" in playlist_id else playlist_id
    client.current_user_unfollow_playlist(playlist_id=playlist_id)
    
    return {"success": True, "message": "Successfully unfollowed playlist", "playlist_id": playlist_id}


# ============================================================================
# ADDITIONAL COMPOSITE TOOLS
# ============================================================================

@mcp.tool(annotations=ToolAnnotations(
    title="Search and Create Playlist",
    readOnlyHint=False,
    idempotentHint=False,
    destructiveHint=False,
    openWorldHint=True
))
async def search_and_create_playlist(
    ctx,
    query: str,
    playlist_name: str,
    limit: int = 20,
    search_type: str = "track",
    description: str = ""
) -> dict:
    """Search for music and create a playlist from the results."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    await ctx.report_progress(0, 3, "Searching...")
    
    results = client.search(q=query, limit=limit, type=search_type)
    
    uris = []
    if search_type == "track" and "tracks" in results:
        uris = [track['uri'] for track in results['tracks']['items']]
    elif search_type == "album" and "albums" in results:
        for album in results['albums']['items'][:limit]:
            album_tracks = client.album_tracks(album['id'], limit=1)
            if album_tracks.get('items'):
                uris.append(album_tracks['items'][0]['uri'])
    elif search_type == "artist" and "artists" in results:
        for artist in results['artists']['items'][:limit]:
            artist_tracks = client.artist_top_tracks(artist['id'])
            if artist_tracks.get('tracks'):
                uris.append(artist_tracks['tracks'][0]['uri'])
    
    if not uris:
        return {"success": False, "message": f"No {search_type}s found for '{query}'"}
    
    await ctx.report_progress(1, 3, "Creating playlist...")
    
    user_info = client.current_user()
    playlist = client.user_playlist_create(
        user=user_info["id"], name=playlist_name, public=True,
        description=description or f"Created from search: {query}"
    )
    
    await ctx.report_progress(2, 3, "Adding tracks...")
    client.playlist_add_items(playlist['id'], uris)
    
    await ctx.report_progress(3, 3, "Complete!")
    
    return {
        "success": True,
        "playlist": {"name": playlist["name"], "uri": playlist["uri"], "id": playlist["id"]},
        "tracks_added": len(uris),
        "search_query": query
    }


@mcp.tool(annotations=ToolAnnotations(
    title="Save Multiple Items",
    readOnlyHint=False,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False
))
async def save_multiple_items(
    ctx,
    track_ids: Optional[List[str]] = None,
    album_ids: Optional[List[str]] = None,
    artist_ids: Optional[List[str]] = None
) -> dict:
    """Save multiple types of items to library in one operation."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    results = {"tracks_saved": 0, "albums_saved": 0, "artists_followed": 0}
    
    if track_ids:
        track_ids = [t.split(":")[-1] if ":" in t else t for t in track_ids]
        client.current_user_saved_tracks_add(track_ids)
        results["tracks_saved"] = len(track_ids)
    
    if album_ids:
        album_ids = [a.split(":")[-1] if ":" in a else a for a in album_ids]
        client.current_user_saved_albums_add(album_ids)
        results["albums_saved"] = len(album_ids)
    
    if artist_ids:
        artist_ids = [a.split(":")[-1] if ":" in a else a for a in artist_ids]
        client.user_follow_artists(artist_ids)
        results["artists_followed"] = len(artist_ids)
    
    return {"success": True, **results}


@mcp.tool(annotations=ToolAnnotations(
    title="Compare User Libraries",
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True
))
async def compare_user_libraries(ctx: Context, user_id: str, limit: int = 50) -> dict:
    """Compare current user's public playlists with another user's playlists."""
    client = ctx.request_context.lifespan_context.spotify_client
    
    user_id = user_id.split(":")[-1] if ":" in user_id else user_id
    
    await ctx.report_progress(0, 2, "Fetching your playlists...")
    my_playlists = client.current_user_playlists(limit=limit)
    
    await ctx.report_progress(1, 2, "Fetching other user's playlists...")
    other_playlists = client.user_playlists(user=user_id, limit=limit)
    
    my_playlist_names = set(p["name"].lower() for p in my_playlists.get("items", []))
    other_playlist_names = set(p["name"].lower() for p in other_playlists.get("items", []))
    
    common = my_playlist_names & other_playlist_names
    
    await ctx.report_progress(2, 2, "Complete!")
    
    return {
        "success": True,
        "my_playlist_count": len(my_playlists.get("items", [])),
        "other_playlist_count": len(other_playlists.get("items", [])),
        "common_playlist_names": list(common),
        "common_count": len(common)
    }


# ============================================================================
# DYNAMIC RESOURCES
# ============================================================================

@mcp.resource("spotify://playback/current")
async def current_playback_resource() -> str:
    """Current playback state resource."""
    client = get_client()
    playback = client.current_playback()
    return json.dumps(playback or {"is_playing": False}, indent=2)


@mcp.resource("spotify://track/{track_id}")
async def track_resource(track_id: str) -> str:
    """Get track by ID."""
    client = get_client()
    track = client.track(track_id)
    return json.dumps(track, indent=2)


@mcp.resource("spotify://playlist/{playlist_id}")
async def playlist_resource(playlist_id: str) -> str:
    """Get playlist by ID."""
    client = get_client()
    playlist = client.playlist(playlist_id)
    return json.dumps(playlist, indent=2)


@mcp.resource("spotify://artist/{artist_id}")
async def artist_resource(artist_id: str) -> str:
    """Get artist by ID."""
    client = get_client()
    artist = client.artist(artist_id)
    return json.dumps(artist, indent=2)


@mcp.resource("spotify://album/{album_id}")
async def album_resource(album_id: str) -> str:
    """Get album by ID."""
    client = get_client()
    album = client.album(album_id)
    return json.dumps(album, indent=2)


@mcp.resource("spotify://show/{show_id}")
async def show_resource(show_id: str) -> str:
    """Get podcast show by ID."""
    client = get_client()
    show = client.show(show_id)
    return json.dumps(show, indent=2)


@mcp.resource("spotify://episode/{episode_id}")
async def episode_resource(episode_id: str) -> str:
    """Get podcast episode by ID."""
    client = get_client()
    episode = client.episode(episode_id)
    return json.dumps(episode, indent=2)


@mcp.resource("spotify://user/top-tracks")
async def user_top_tracks_resource() -> str:
    """Get user's top tracks."""
    client = get_client()
    tracks = client.current_user_top_tracks(limit=20)
    return json.dumps(tracks, indent=2)


@mcp.resource("spotify://user/top-artists")
async def user_top_artists_resource() -> str:
    """Get user's top artists."""
    client = get_client()
    artists = client.current_user_top_artists(limit=20)
    return json.dumps(artists, indent=2)


@mcp.resource("spotify://user/recently-played")
async def user_recently_played_resource() -> str:
    """Get user's recently played tracks."""
    client = get_client()
    recent = client.current_user_recently_played(limit=20)
    return json.dumps(recent, indent=2)


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run the FastMCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
