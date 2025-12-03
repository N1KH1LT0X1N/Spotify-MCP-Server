"""Track operations for Spotify.

Note: Audio Features and Audio Analysis endpoints were deprecated by Spotify
on November 27, 2024 for new development mode applications.
"""

from typing import List, Dict, Any, Optional
from spotify_mcp.spotify_client import SpotifyClient


def get_track(client: SpotifyClient, track_id: str, market: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed information about a track.
    
    Args:
        track_id: Track ID or URI
        market: ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB')
    
    Returns:
        Track details
    """
    # Extract ID from URI if needed
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


def get_several_tracks(client: SpotifyClient, track_ids: List[str], 
                      market: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed information about multiple tracks.
    
    Args:
        track_ids: List of track IDs or URIs (up to 50)
        market: ISO 3166-1 alpha-2 country code
    
    Returns:
        List of track details
    """
    if not track_ids:
        raise ValueError("track_ids cannot be empty")
    
    if len(track_ids) > 50:
        raise ValueError("Cannot retrieve more than 50 tracks at once")
    
    # Extract IDs from URIs if needed
    track_ids = [t.split(":")[-1] if ":" in t else t for t in track_ids]
    
    result = client.tracks(track_ids, market)
    
    tracks = []
    for track in result.get("tracks", []):
        if track:  # Some might be None if not available
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


# Tool definitions for MCP
TRACK_TOOLS = [
    {
        "name": "get_track",
        "description": "Get detailed information about a track including artists, album, duration, and popularity.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "track_id": {
                    "type": "string",
                    "description": "Track ID or URI (e.g., 'spotify:track:xxx' or 'trackid')"
                },
                "market": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB')"
                }
            },
            "required": ["track_id"]
        }
    },
    {
        "name": "get_several_tracks",
        "description": "Get detailed information about multiple tracks at once.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "track_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of track IDs or URIs (e.g., ['spotify:track:xxx']). Maximum 50 tracks.",
                    "minItems": 1,
                    "maxItems": 50
                },
                "market": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code"
                }
            },
            "required": ["track_ids"]
        }
    }
]
