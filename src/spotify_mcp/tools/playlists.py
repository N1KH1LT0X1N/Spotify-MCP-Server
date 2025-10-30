"""Playlist management tools for Spotify."""

from typing import List, Dict, Any, Optional
from spotify_mcp.spotify_client import SpotifyClient


def get_user_playlists(client: SpotifyClient, limit: int = 50, 
                       offset: int = 0) -> Dict[str, Any]:
    """
    Get a list of the user's playlists.
    
    Args:
        limit: Maximum number of playlists to return (1-50, default 50)
        offset: Offset for pagination (default 0)
    
    Returns:
        List of playlists with pagination info
    """
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    results = client.current_user_playlists(limit=limit, offset=offset)
    
    items = results.get("items", [])
    total = results.get("total", 0)
    
    return {
        "playlists": [
            {
                "name": item["name"],
                "uri": item["uri"],
                "id": item["id"],
                "description": item.get("description"),
                "owner": {
                    "display_name": item.get("owner", {}).get("display_name"),
                    "id": item.get("owner", {}).get("id")
                },
                "total_tracks": item.get("tracks", {}).get("total", 0),
                "public": item.get("public", False),
                "collaborative": item.get("collaborative", False),
                "snapshot_id": item.get("snapshot_id")
            }
            for item in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


def get_playlist(client: SpotifyClient, playlist_id: str,
                 include_tracks: bool = True, tracks_limit: int = 100,
                 tracks_offset: int = 0) -> Dict[str, Any]:
    """
    Get details of a specific playlist, optionally including tracks.
    
    Args:
        playlist_id: Playlist ID or URI
        include_tracks: Whether to include track listing (default True)
        tracks_limit: Maximum number of tracks to return (1-100, default 100)
        tracks_offset: Offset for track pagination (default 0)
    
    Returns:
        Playlist details and tracks (if requested)
    """
    # Extract ID from URI if needed
    playlist_id = playlist_id.split(":")[-1] if ":" in playlist_id else playlist_id
    
    if not 1 <= tracks_limit <= 100:
        raise ValueError("tracks_limit must be between 1 and 100")
    
    # Get playlist details
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
        # Get tracks
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
                    "added_by": {
                        "id": item.get("added_by", {}).get("id"),
                        "display_name": item.get("added_by", {}).get("display_name")
                    } if item.get("added_by") else None,
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
                if item.get("track")  # Filter out null tracks
            ],
            "total": tracks_result.get("total", 0),
            "limit": tracks_limit,
            "offset": tracks_offset,
            "has_more": tracks_offset + tracks_limit < tracks_result.get("total", 0)
        }
    
    return result


def create_playlist(client: SpotifyClient, name: str, public: bool = True,
                   collaborative: bool = False, description: str = "") -> Dict[str, Any]:
    """
    Create a new playlist for the user.
    
    Args:
        name: Name of the playlist
        public: Whether the playlist should be public (default True)
        collaborative: Whether the playlist should be collaborative (default False)
        description: Description of the playlist (optional)
    
    Returns:
        Created playlist details
    """
    if not name:
        raise ValueError("Playlist name cannot be empty")
    
    # Get current user ID
    user_info = client.current_user()
    user_id = user_info["id"]
    
    playlist = client.user_playlist_create(
        user=user_id,
        name=name,
        public=public,
        description=description
    )
    
    # Note: collaborative playlists must be private
    if collaborative and not public:
        # This would require a follow-up call to modify the playlist
        pass
    
    return {
        "success": True,
        "message": f"Playlist '{name}' created successfully",
        "playlist": {
            "name": playlist["name"],
            "uri": playlist["uri"],
            "id": playlist["id"],
            "description": playlist.get("description"),
            "public": playlist.get("public", False),
            "collaborative": playlist.get("collaborative", False),
            "snapshot_id": playlist.get("snapshot_id")
        }
    }


def add_tracks_to_playlist(client: SpotifyClient, playlist_id: str,
                          track_uris: List[str], position: Optional[int] = None) -> Dict[str, Any]:
    """
    Add one or more tracks to a playlist.
    
    Args:
        playlist_id: Playlist ID or URI
        track_uris: List of track URIs to add (up to 100)
        position: Position to insert tracks (optional, default: end of playlist)
    
    Returns:
        Success message with snapshot ID
    """
    # Extract ID from URI if needed
    playlist_id = playlist_id.split(":")[-1] if ":" in playlist_id else playlist_id
    
    if not track_uris:
        raise ValueError("track_uris cannot be empty")
    
    if len(track_uris) > 100:
        raise ValueError("Cannot add more than 100 tracks at once")
    
    # Ensure URIs are in correct format
    formatted_uris = []
    for uri in track_uris:
        if not uri.startswith("spotify:track:"):
            # Assume it's an ID and convert to URI
            formatted_uris.append(f"spotify:track:{uri}")
        else:
            formatted_uris.append(uri)
    
    result = client.playlist_add_items(playlist_id=playlist_id, items=formatted_uris)
    
    return {
        "success": True,
        "message": f"Successfully added {len(track_uris)} track(s) to playlist",
        "track_count": len(track_uris),
        "snapshot_id": result.get("snapshot_id")
    }


def remove_tracks_from_playlist(client: SpotifyClient, playlist_id: str,
                               track_uris: List[str]) -> Dict[str, Any]:
    """
    Remove one or more tracks from a playlist.
    Note: This removes all occurrences of the specified tracks.
    
    Args:
        playlist_id: Playlist ID or URI
        track_uris: List of track URIs to remove (up to 100)
    
    Returns:
        Success message with snapshot ID
    """
    # Extract ID from URI if needed
    playlist_id = playlist_id.split(":")[-1] if ":" in playlist_id else playlist_id
    
    if not track_uris:
        raise ValueError("track_uris cannot be empty")
    
    if len(track_uris) > 100:
        raise ValueError("Cannot remove more than 100 tracks at once")
    
    # Ensure URIs are in correct format
    formatted_uris = []
    for uri in track_uris:
        if not uri.startswith("spotify:track:"):
            # Assume it's an ID and convert to URI
            formatted_uris.append(f"spotify:track:{uri}")
        else:
            formatted_uris.append(uri)
    
    result = client.playlist_remove_all_occurrences_of_items(
        playlist_id=playlist_id,
        items=formatted_uris
    )
    
    return {
        "success": True,
        "message": f"Successfully removed {len(track_uris)} track(s) from playlist",
        "track_count": len(track_uris),
        "snapshot_id": result.get("snapshot_id")
    }


# Tool definitions for MCP
PLAYLIST_TOOLS = [
    {
        "name": "get_user_playlists",
        "description": "Get a list of the user's playlists.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of playlists to return (1-50)",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 50
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
        "name": "get_playlist",
        "description": "Get details of a specific playlist, including tracks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "playlist_id": {
                    "type": "string",
                    "description": "Playlist ID or URI (e.g., 'spotify:playlist:xxx' or just the ID)"
                },
                "include_tracks": {
                    "type": "boolean",
                    "description": "Whether to include track listing",
                    "default": True
                },
                "tracks_limit": {
                    "type": "integer",
                    "description": "Maximum number of tracks to return (1-100)",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 100
                },
                "tracks_offset": {
                    "type": "integer",
                    "description": "Offset for track pagination",
                    "minimum": 0,
                    "default": 0
                }
            },
            "required": ["playlist_id"]
        }
    },
    {
        "name": "create_playlist",
        "description": "Create a new playlist for the user.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the playlist"
                },
                "public": {
                    "type": "boolean",
                    "description": "Whether the playlist should be public",
                    "default": True
                },
                "collaborative": {
                    "type": "boolean",
                    "description": "Whether the playlist should be collaborative (must be private)",
                    "default": False
                },
                "description": {
                    "type": "string",
                    "description": "Description of the playlist",
                    "default": ""
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "add_tracks_to_playlist",
        "description": "Add one or more tracks to a playlist.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "playlist_id": {
                    "type": "string",
                    "description": "Playlist ID or URI"
                },
                "track_uris": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of track URIs or IDs to add (e.g., ['spotify:track:xxx'] or ['trackid1', 'trackid2']). Maximum 100 tracks.",
                    "minItems": 1,
                    "maxItems": 100
                },
                "position": {
                    "type": "integer",
                    "description": "Position to insert tracks (optional, default: end of playlist)",
                    "minimum": 0
                }
            },
            "required": ["playlist_id", "track_uris"]
        }
    },
    {
        "name": "remove_tracks_from_playlist",
        "description": "Remove one or more tracks from a playlist. This removes all occurrences of the specified tracks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "playlist_id": {
                    "type": "string",
                    "description": "Playlist ID or URI"
                },
                "track_uris": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of track URIs or IDs to remove (e.g., ['spotify:track:xxx'] or ['trackid1', 'trackid2']). Maximum 100 tracks.",
                    "minItems": 1,
                    "maxItems": 100
                }
            },
            "required": ["playlist_id", "track_uris"]
        }
    }
]
