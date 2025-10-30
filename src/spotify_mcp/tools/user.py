"""User profile and statistics tools for Spotify."""

from typing import Dict, Any
from spotify_mcp.spotify_client import SpotifyClient


def get_current_user(client: SpotifyClient) -> Dict[str, Any]:
    """
    Get the current user's Spotify profile information.
    
    Returns:
        User profile including display name, email, subscription type, etc.
    """
    user = client.current_user()
    
    return {
        "id": user.get("id"),
        "display_name": user.get("display_name"),
        "email": user.get("email"),
        "country": user.get("country"),
        "product": user.get("product"),  # premium, free, etc.
        "followers": user.get("followers", {}).get("total", 0),
        "external_urls": user.get("external_urls", {}),
        "uri": user.get("uri")
    }


def get_top_items(client: SpotifyClient, item_type: str = "tracks",
                  time_range: str = "medium_term", limit: int = 20,
                  offset: int = 0) -> Dict[str, Any]:
    """
    Get the user's top tracks or artists.
    
    Args:
        item_type: Type of items - "tracks" or "artists"
        time_range: Time range for top items:
                   - "short_term" (last 4 weeks)
                   - "medium_term" (last 6 months, default)
                   - "long_term" (several years)
        limit: Maximum number of items to return (1-50, default 20)
        offset: Offset for pagination (default 0)
    
    Returns:
        List of top tracks or artists
    """
    valid_types = ["tracks", "artists"]
    if item_type not in valid_types:
        raise ValueError(f"item_type must be one of: {', '.join(valid_types)}")
    
    valid_ranges = ["short_term", "medium_term", "long_term"]
    if time_range not in valid_ranges:
        raise ValueError(f"time_range must be one of: {', '.join(valid_ranges)}")
    
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    if item_type == "tracks":
        results = client.current_user_top_tracks(
            limit=limit,
            offset=offset,
            time_range=time_range
        )
        
        items = results.get("items", [])
        total = results.get("total", 0)
        
        formatted_items = [
            {
                "name": item["name"],
                "uri": item["uri"],
                "id": item["id"],
                "artists": [
                    {"name": a["name"], "uri": a["uri"]} 
                    for a in item.get("artists", [])
                ],
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
    else:  # artists
        results = client.current_user_top_artists(
            limit=limit,
            offset=offset,
            time_range=time_range
        )
        
        items = results.get("items", [])
        total = results.get("total", 0)
        
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
    
    # Create friendly time range description
    time_range_descriptions = {
        "short_term": "last 4 weeks",
        "medium_term": "last 6 months",
        "long_term": "all time"
    }
    
    return {
        "type": item_type,
        "time_range": time_range,
        "time_range_description": time_range_descriptions[time_range],
        "items": formatted_items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


# Tool definitions for MCP
USER_TOOLS = [
    {
        "name": "get_current_user",
        "description": "Get the current user's Spotify profile information.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_top_items",
        "description": "Get the user's top tracks or artists over different time periods.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item_type": {
                    "type": "string",
                    "enum": ["tracks", "artists"],
                    "description": "Type of items to retrieve",
                    "default": "tracks"
                },
                "time_range": {
                    "type": "string",
                    "enum": ["short_term", "medium_term", "long_term"],
                    "description": "Time range: 'short_term' (last 4 weeks), 'medium_term' (last 6 months), 'long_term' (all time)",
                    "default": "medium_term"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of items to return (1-50)",
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
    }
]
