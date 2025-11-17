"""Album management tools for Spotify."""

from typing import List, Dict, Any, Optional
from spotify_mcp.spotify_client import SpotifyClient


def get_album(client: SpotifyClient, album_id: str) -> Dict[str, Any]:
    """
    Get Spotify catalog information for a single album.
    
    Args:
        album_id: The Spotify ID or URI for the album
    
    Returns:
        Album details including tracks, artists, and metadata
    """
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


def get_several_albums(client: SpotifyClient, album_ids: List[str]) -> Dict[str, Any]:
    """
    Get Spotify catalog information for multiple albums.
    
    Args:
        album_ids: List of album IDs or URIs (up to 20)
    
    Returns:
        List of album details
    """
    if not album_ids:
        raise ValueError("album_ids cannot be empty")
    
    if len(album_ids) > 20:
        raise ValueError("Cannot get more than 20 albums at once")
    
    # Extract IDs from URIs if needed
    album_ids = [a.split(":")[-1] if ":" in a else a for a in album_ids]
    
    results = client.albums(album_ids)
    
    albums = []
    for album in results.get("albums", []):
        if album is None:
            continue
            
        albums.append({
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
            "images": album.get("images", []),
            "external_urls": album.get("external_urls", {})
        })
    
    return {
        "albums": albums,
        "total": len(albums)
    }


def get_album_tracks(client: SpotifyClient, album_id: str, limit: int = 50, 
                     offset: int = 0) -> Dict[str, Any]:
    """
    Get Spotify catalog information about an album's tracks.
    
    Args:
        album_id: The Spotify ID or URI for the album
        limit: Maximum number of tracks to return (1-50, default 50)
        offset: Offset for pagination (default 0)
    
    Returns:
        List of album tracks with pagination info
    """
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    # Extract ID from URI if needed
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


def get_saved_albums(client: SpotifyClient, limit: int = 20, 
                     offset: int = 0) -> Dict[str, Any]:
    """
    Get the user's saved (liked) albums.
    
    Args:
        limit: Maximum number of albums to return (1-50, default 20)
        offset: Offset for pagination (default 0)
    
    Returns:
        List of saved albums with pagination info
    """
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


def save_albums(client: SpotifyClient, album_ids: List[str]) -> Dict[str, Any]:
    """
    Save (like) one or more albums to the user's library.
    
    Args:
        album_ids: List of album IDs or URIs to save (up to 50)
    
    Returns:
        Success message with count of saved albums
    """
    if not album_ids:
        raise ValueError("album_ids cannot be empty")
    
    if len(album_ids) > 50:
        raise ValueError("Cannot save more than 50 albums at once")
    
    # Extract IDs from URIs if needed
    album_ids = [a.split(":")[-1] if ":" in a else a for a in album_ids]
    
    client.current_user_saved_albums_add(albums=album_ids)
    
    return {
        "success": True,
        "message": f"Successfully saved {len(album_ids)} album(s)",
        "album_count": len(album_ids),
        "album_ids": album_ids
    }


def remove_saved_albums(client: SpotifyClient, album_ids: List[str]) -> Dict[str, Any]:
    """
    Remove (unlike) one or more albums from the user's library.
    
    Args:
        album_ids: List of album IDs or URIs to remove (up to 50)
    
    Returns:
        Success message with count of removed albums
    """
    if not album_ids:
        raise ValueError("album_ids cannot be empty")
    
    if len(album_ids) > 50:
        raise ValueError("Cannot remove more than 50 albums at once")
    
    # Extract IDs from URIs if needed
    album_ids = [a.split(":")[-1] if ":" in a else a for a in album_ids]
    
    client.current_user_saved_albums_delete(albums=album_ids)
    
    return {
        "success": True,
        "message": f"Successfully removed {len(album_ids)} album(s)",
        "album_count": len(album_ids),
        "album_ids": album_ids
    }


def check_saved_albums(client: SpotifyClient, album_ids: List[str]) -> Dict[str, Any]:
    """
    Check if one or more albums are saved in the user's library.
    
    Args:
        album_ids: List of album IDs or URIs to check (up to 20)
    
    Returns:
        List indicating which albums are saved
    """
    if not album_ids:
        raise ValueError("album_ids cannot be empty")
    
    if len(album_ids) > 20:
        raise ValueError("Cannot check more than 20 albums at once")
    
    # Extract IDs from URIs if needed
    album_ids = [a.split(":")[-1] if ":" in a else a for a in album_ids]
    
    results = client.current_user_saved_albums_contains(albums=album_ids)
    
    return {
        "albums": [
            {
                "album_id": album_id,
                "is_saved": is_saved
            }
            for album_id, is_saved in zip(album_ids, results)
        ],
        "total_checked": len(album_ids),
        "total_saved": sum(results)
    }


def get_new_releases(client: SpotifyClient, limit: int = 20, 
                     offset: int = 0, country: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a list of new album releases featured in Spotify.
    
    Args:
        limit: Maximum number of albums to return (1-50, default 20)
        offset: Offset for pagination (default 0)
        country: ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB')
    
    Returns:
        List of new album releases
    """
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    kwargs = {"limit": limit, "offset": offset}
    if country:
        kwargs["country"] = country
    
    results = client.new_releases(**kwargs)
    
    albums_data = results.get("albums", {})
    items = albums_data.get("items", [])
    total = albums_data.get("total", 0)
    
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
                "images": album.get("images", []),
                "external_urls": album.get("external_urls", {})
            }
            for album in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


# Tool definitions for MCP
ALBUM_TOOLS = [
    {
        "name": "get_album",
        "description": "Get Spotify catalog information for a single album.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "album_id": {
                    "type": "string",
                    "description": "The Spotify ID or URI for the album"
                }
            },
            "required": ["album_id"]
        }
    },
    {
        "name": "get_several_albums",
        "description": "Get Spotify catalog information for multiple albums in a single request (more efficient than multiple get_album calls).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "album_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of album IDs or URIs (e.g., ['spotify:album:xxx'] or ['albumid1', 'albumid2']). Maximum 20 albums.",
                    "minItems": 1,
                    "maxItems": 20
                }
            },
            "required": ["album_ids"]
        }
    },
    {
        "name": "get_album_tracks",
        "description": "Get Spotify catalog information about an album's tracks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "album_id": {
                    "type": "string",
                    "description": "The Spotify ID or URI for the album"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of tracks to return (1-50)",
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
            },
            "required": ["album_id"]
        }
    },
    {
        "name": "get_saved_albums",
        "description": "Get the user's saved (liked) albums from their library.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of albums to return (1-50)",
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
        "name": "save_albums",
        "description": "Save (like) one or more albums to the user's library.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "album_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of album IDs or URIs to save (e.g., ['spotify:album:xxx'] or ['albumid1', 'albumid2']). Maximum 50 albums.",
                    "minItems": 1,
                    "maxItems": 50
                }
            },
            "required": ["album_ids"]
        }
    },
    {
        "name": "remove_saved_albums",
        "description": "Remove (unlike) one or more albums from the user's library.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "album_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of album IDs or URIs to remove (e.g., ['spotify:album:xxx'] or ['albumid1', 'albumid2']). Maximum 50 albums.",
                    "minItems": 1,
                    "maxItems": 50
                }
            },
            "required": ["album_ids"]
        }
    },
    {
        "name": "check_saved_albums",
        "description": "Check if one or more albums are saved in the user's library.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "album_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of album IDs or URIs to check (e.g., ['spotify:album:xxx'] or ['albumid1', 'albumid2']). Maximum 20 albums.",
                    "minItems": 1,
                    "maxItems": 20
                }
            },
            "required": ["album_ids"]
        }
    },
    {
        "name": "get_new_releases",
        "description": "Get a list of new album releases featured in Spotify.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of albums to return (1-50)",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 20
                },
                "offset": {
                    "type": "integer",
                    "description": "Offset for pagination",
                    "minimum": 0,
                    "default": 0
                },
                "country": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB') to get releases for a specific market"
                }
            }
        }
    }
]
