"""Search tools for Spotify.

Note: Recommendations endpoint was deprecated by Spotify on November 27, 2024
for new development mode applications.
"""

from typing import Optional, Dict, Any
from spotify_mcp.spotify_client import SpotifyClient


def search(client: SpotifyClient, query: str, search_type: str = "track", 
           limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    Search for tracks, albums, artists, or playlists.
    
    Args:
        query: Search query
        search_type: Type to search for - "track", "album", "artist", or "playlist"
        limit: Maximum number of results (1-50, default 20)
        offset: Offset for pagination (default 0)
    
    Returns:
        Search results with items and pagination info
    """
    valid_types = ["track", "album", "artist", "playlist"]
    if search_type not in valid_types:
        raise ValueError(f"search_type must be one of: {', '.join(valid_types)}")
    
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    results = client.search(q=query, limit=limit, offset=offset, type=search_type)
    
    # Format results based on type
    key = f"{search_type}s"
    items = results.get(key, {}).get("items", [])
    total = results.get(key, {}).get("total", 0)
    
    formatted_items = []
    
    if search_type == "track":
        formatted_items = [
            {
                "name": item["name"],
                "uri": item["uri"],
                "id": item["id"],
                "artists": [{"name": a["name"], "uri": a["uri"]} for a in item.get("artists", [])],
                "album": {
                    "name": item.get("album", {}).get("name"),
                    "uri": item.get("album", {}).get("uri"),
                },
                "duration_ms": item.get("duration_ms"),
                "explicit": item.get("explicit", False),
                "popularity": item.get("popularity", 0)
            }
            for item in items
        ]
    elif search_type == "album":
        formatted_items = [
            {
                "name": item["name"],
                "uri": item["uri"],
                "id": item["id"],
                "artists": [{"name": a["name"], "uri": a["uri"]} for a in item.get("artists", [])],
                "release_date": item.get("release_date"),
                "total_tracks": item.get("total_tracks"),
                "album_type": item.get("album_type")
            }
            for item in items
        ]
    elif search_type == "artist":
        formatted_items = [
            {
                "name": item["name"],
                "uri": item["uri"],
                "id": item["id"],
                "genres": item.get("genres", []),
                "popularity": item.get("popularity", 0),
                "followers": item.get("followers", {}).get("total", 0)
            }
            for item in items
        ]
    elif search_type == "playlist":
        formatted_items = [
            {
                "name": item["name"],
                "uri": item["uri"],
                "id": item["id"],
                "owner": {
                    "display_name": item.get("owner", {}).get("display_name"),
                    "id": item.get("owner", {}).get("id")
                },
                "description": item.get("description"),
                "total_tracks": item.get("tracks", {}).get("total", 0),
                "public": item.get("public", False)
            }
            for item in items
        ]
    
    return {
        "query": query,
        "type": search_type,
        "items": formatted_items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


# Tool definitions for MCP
SEARCH_TOOLS = [
    {
        "name": "search",
        "description": "Search for tracks, albums, artists, or playlists on Spotify.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'Bohemian Rhapsody', 'The Beatles', 'rock playlist')"
                },
                "search_type": {
                    "type": "string",
                    "enum": ["track", "album", "artist", "playlist"],
                    "description": "Type of item to search for",
                    "default": "track"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (1-50)",
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
            "required": ["query"]
        }
    }
]
