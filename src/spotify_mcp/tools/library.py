"""Library management tools for Spotify."""

from typing import List, Dict, Any, Optional
from spotify_mcp.spotify_client import SpotifyClient


def get_saved_tracks(client: SpotifyClient, limit: int = 20, 
                     offset: int = 0) -> Dict[str, Any]:
    """
    Get the user's saved (liked) tracks.
    
    Args:
        limit: Maximum number of tracks to return (1-50, default 20)
        offset: Offset for pagination (default 0)
    
    Returns:
        List of saved tracks with pagination info
    """
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    results = client.current_user_saved_tracks(limit=limit, offset=offset)
    
    items = results.get("items", [])
    total = results.get("total", 0)
    
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
                        "uri": item["track"].get("album", {}).get("uri"),
                    },
                    "duration_ms": item["track"].get("duration_ms"),
                    "explicit": item["track"].get("explicit", False),
                    "popularity": item["track"].get("popularity", 0)
                }
            }
            for item in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


def save_tracks(client: SpotifyClient, track_ids: List[str]) -> Dict[str, Any]:
    """
    Save (like) one or more tracks to the user's library.
    
    Args:
        track_ids: List of track IDs or URIs to save (up to 50)
    
    Returns:
        Success message with count of saved tracks
    """
    if not track_ids:
        raise ValueError("track_ids cannot be empty")
    
    if len(track_ids) > 50:
        raise ValueError("Cannot save more than 50 tracks at once")
    
    # Extract IDs from URIs if needed
    track_ids = [t.split(":")[-1] if ":" in t else t for t in track_ids]
    
    client.current_user_saved_tracks_add(tracks=track_ids)
    
    return {
        "success": True,
        "message": f"Successfully saved {len(track_ids)} track(s)",
        "track_count": len(track_ids),
        "track_ids": track_ids
    }


def remove_saved_tracks(client: SpotifyClient, track_ids: List[str]) -> Dict[str, Any]:
    """
    Remove (unlike) one or more tracks from the user's library.
    
    Args:
        track_ids: List of track IDs or URIs to remove (up to 50)
    
    Returns:
        Success message with count of removed tracks
    """
    if not track_ids:
        raise ValueError("track_ids cannot be empty")
    
    if len(track_ids) > 50:
        raise ValueError("Cannot remove more than 50 tracks at once")
    
    # Extract IDs from URIs if needed
    track_ids = [t.split(":")[-1] if ":" in t else t for t in track_ids]
    
    client.current_user_saved_tracks_delete(tracks=track_ids)
    
    return {
        "success": True,
        "message": f"Successfully removed {len(track_ids)} track(s)",
        "track_count": len(track_ids),
        "track_ids": track_ids
    }


def check_saved_tracks(client: SpotifyClient, track_ids: List[str]) -> Dict[str, Any]:
    """
    Check if one or more tracks are saved in the user's library.
    
    Args:
        track_ids: List of track IDs or URIs to check (up to 50)
    
    Returns:
        List indicating which tracks are saved
    """
    if not track_ids:
        raise ValueError("track_ids cannot be empty")
    
    if len(track_ids) > 50:
        raise ValueError("Cannot check more than 50 tracks at once")
    
    # Extract IDs from URIs if needed
    track_ids = [t.split(":")[-1] if ":" in t else t for t in track_ids]
    
    results = client.current_user_saved_tracks_contains(tracks=track_ids)
    
    return {
        "tracks": [
            {
                "track_id": track_id,
                "is_saved": is_saved
            }
            for track_id, is_saved in zip(track_ids, results)
        ],
        "total_checked": len(track_ids),
        "total_saved": sum(results)
    }


# Tool definitions for MCP
LIBRARY_TOOLS = [
    {
        "name": "get_saved_tracks",
        "description": "Get the user's saved (liked) tracks from their library.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of tracks to return (1-50)",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 20
                },
                "offset": {
                    "type": "integer",
                    "description": "Offset for pagination",
                    "minimum": 0,
                    "default": 0
                }
            }
        }
    },
    {
        "name": "save_tracks",
        "description": "Save (like) one or more tracks to the user's library.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "track_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of track IDs or URIs to save (e.g., ['spotify:track:xxx'] or ['trackid1', 'trackid2']). Maximum 50 tracks.",
                    "minItems": 1,
                    "maxItems": 50
                }
            },
            "required": ["track_ids"]
        }
    },
    {
        "name": "remove_saved_tracks",
        "description": "Remove (unlike) one or more tracks from the user's library.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "track_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of track IDs or URIs to remove (e.g., ['spotify:track:xxx'] or ['trackid1', 'trackid2']). Maximum 50 tracks.",
                    "minItems": 1,
                    "maxItems": 50
                }
            },
            "required": ["track_ids"]
        }
    },
    {
        "name": "check_saved_tracks",
        "description": "Check if one or more tracks are saved in the user's library.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "track_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of track IDs or URIs to check (e.g., ['spotify:track:xxx'] or ['trackid1', 'trackid2']). Maximum 50 tracks.",
                    "minItems": 1,
                    "maxItems": 50
                }
            },
            "required": ["track_ids"]
        }
    }
]
