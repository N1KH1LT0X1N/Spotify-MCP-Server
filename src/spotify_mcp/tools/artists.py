"""Artist information and discovery tools for Spotify.

Note: Related Artists endpoint was deprecated by Spotify on November 27, 2024
for new development mode applications.
"""

from typing import List, Dict, Any, Optional
from spotify_mcp.spotify_client import SpotifyClient


def get_artist(client: SpotifyClient, artist_id: str) -> Dict[str, Any]:
    """
    Get Spotify catalog information for a single artist.
    
    Args:
        artist_id: The Spotify ID or URI for the artist
    
    Returns:
        Artist details including genres, popularity, followers, and images
    """
    # Extract ID from URI if needed
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


def get_several_artists(client: SpotifyClient, artist_ids: List[str]) -> Dict[str, Any]:
    """
    Get Spotify catalog information for multiple artists.
    
    Args:
        artist_ids: List of Spotify IDs or URIs for the artists (max 50)
    
    Returns:
        List of artist details
    """
    if not artist_ids:
        raise ValueError("artist_ids cannot be empty")
    
    if len(artist_ids) > 50:
        raise ValueError("Cannot request more than 50 artists at once")
    
    # Extract IDs from URIs if needed
    artist_ids = [aid.split(":")[-1] if ":" in aid else aid for aid in artist_ids]
    
    results = client.artists(artist_ids)
    artists = results.get("artists", [])
    
    return {
        "artists": [
            {
                "id": artist["id"],
                "uri": artist["uri"],
                "name": artist["name"],
                "genres": artist.get("genres", []),
                "popularity": artist.get("popularity", 0),
                "followers": artist.get("followers", {}).get("total", 0),
                "images": artist.get("images", []),
                "external_urls": artist.get("external_urls", {})
            }
            for artist in artists if artist is not None
        ],
        "total": len(artists)
    }


def get_artist_albums(client: SpotifyClient, artist_id: str, 
                      include_groups: Optional[List[str]] = None,
                      limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    Get Spotify catalog information about an artist's albums.
    
    Args:
        artist_id: The Spotify ID or URI for the artist
        include_groups: List of album types to include: "album", "single", "appears_on", "compilation"
        limit: Maximum number of albums to return (1-50, default 20)
        offset: Offset for pagination (default 0)
    
    Returns:
        List of albums by the artist
    """
    # Extract ID from URI if needed
    artist_id = artist_id.split(":")[-1] if ":" in artist_id else artist_id
    
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    # Validate include_groups
    valid_groups = ["album", "single", "appears_on", "compilation"]
    if include_groups:
        invalid = [g for g in include_groups if g not in valid_groups]
        if invalid:
            raise ValueError(f"Invalid include_groups: {invalid}. Must be one of: {valid_groups}")
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
                "external_urls": album.get("external_urls", {}),
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


def get_artist_top_tracks(client: SpotifyClient, artist_id: str, 
                         market: str = "US") -> Dict[str, Any]:
    """
    Get Spotify catalog information about an artist's top tracks.
    
    Args:
        artist_id: The Spotify ID or URI for the artist
        market: ISO 3166-1 alpha-2 country code (e.g., "US", "GB", "CA")
    
    Returns:
        List of the artist's top tracks in the specified market
    """
    # Extract ID from URI if needed
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
                "external_urls": track.get("external_urls", {}),
                "preview_url": track.get("preview_url")
            }
            for track in tracks
        ],
        "total": len(tracks)
    }


# Tool definitions for MCP
ARTIST_TOOLS = [
    {
        "name": "get_artist",
        "description": "Get detailed information about a single artist including genres, popularity, followers, and images.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "artist_id": {
                    "type": "string",
                    "description": "The Spotify ID or URI for the artist"
                }
            },
            "required": ["artist_id"]
        }
    },
    {
        "name": "get_several_artists",
        "description": "Get information about multiple artists in a single request (up to 50 artists).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "artist_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of Spotify IDs or URIs for the artists (max 50)",
                    "minItems": 1,
                    "maxItems": 50
                }
            },
            "required": ["artist_ids"]
        }
    },
    {
        "name": "get_artist_albums",
        "description": "Get an artist's albums, singles, compilations, and appearances on other albums.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "artist_id": {
                    "type": "string",
                    "description": "The Spotify ID or URI for the artist"
                },
                "include_groups": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["album", "single", "appears_on", "compilation"]
                    },
                    "description": "Filter by album types. If omitted, all types are returned."
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of albums (1-50)",
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
            },
            "required": ["artist_id"]
        }
    },
    {
        "name": "get_artist_top_tracks",
        "description": "Get an artist's top 10 most popular tracks in a specific market/country.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "artist_id": {
                    "type": "string",
                    "description": "The Spotify ID or URI for the artist"
                },
                "market": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB', 'CA', 'DE', 'FR')",
                    "default": "US"
                }
            },
            "required": ["artist_id"]
        }
    }
]
