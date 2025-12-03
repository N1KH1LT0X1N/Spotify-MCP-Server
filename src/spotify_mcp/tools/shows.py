"""Show (podcast) management tools for Spotify."""

from typing import List, Dict, Any, Optional
from spotify_mcp.spotify_client import SpotifyClient


def get_show(client: SpotifyClient, show_id: str, market: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed information about a show (podcast).
    
    Args:
        show_id: Show ID or URI
        market: ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB')
    
    Returns:
        Show details including episodes
    """
    # Extract ID from URI if needed
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


def get_several_shows(client: SpotifyClient, show_ids: List[str], 
                     market: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed information about multiple shows.
    
    Args:
        show_ids: List of show IDs or URIs (up to 50)
        market: ISO 3166-1 alpha-2 country code
    
    Returns:
        List of show details
    """
    if not show_ids:
        raise ValueError("show_ids cannot be empty")
    
    if len(show_ids) > 50:
        raise ValueError("Cannot retrieve more than 50 shows at once")
    
    # Extract IDs from URIs if needed
    show_ids = [s.split(":")[-1] if ":" in s else s for s in show_ids]
    
    result = client.shows(show_ids, market)
    
    shows = []
    for show in result.get("shows", []):
        if show:  # Some might be None if not available
            shows.append({
                "id": show.get("id"),
                "uri": show.get("uri"),
                "name": show.get("name"),
                "description": show.get("description"),
                "publisher": show.get("publisher"),
                "total_episodes": show.get("total_episodes", 0),
                "explicit": show.get("explicit", False),
                "images": show.get("images", [])
            })
    
    return {
        "success": True,
        "shows": shows,
        "total": len(shows)
    }


def get_show_episodes(client: SpotifyClient, show_id: str, limit: int = 20, 
                     offset: int = 0, market: Optional[str] = None) -> Dict[str, Any]:
    """
    Get episodes from a show (podcast).
    
    Args:
        show_id: Show ID or URI
        limit: Maximum number of episodes to return (1-50, default 20)
        offset: Offset for pagination (default 0)
        market: ISO 3166-1 alpha-2 country code
    
    Returns:
        List of episodes with pagination info
    """
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    # Extract ID from URI if needed
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
                "images": ep.get("images", []),
                "external_urls": ep.get("external_urls", {})
            }
            for ep in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


def get_saved_shows(client: SpotifyClient, limit: int = 20, 
                   offset: int = 0) -> Dict[str, Any]:
    """
    Get user's saved shows (podcasts).
    
    Args:
        limit: Maximum number of shows to return (1-50, default 20)
        offset: Offset for pagination (default 0)
    
    Returns:
        List of saved shows with pagination info
    """
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    result = client.current_user_saved_shows(limit=limit, offset=offset)
    
    items = result.get("items", [])
    total = result.get("total", 0)
    
    return {
        "success": True,
        "shows": [
            {
                "added_at": item.get("added_at"),
                "show": {
                    "id": item["show"]["id"],
                    "uri": item["show"]["uri"],
                    "name": item["show"]["name"],
                    "description": item["show"]["description"],
                    "publisher": item["show"].get("publisher"),
                    "total_episodes": item["show"].get("total_episodes", 0),
                    "explicit": item["show"].get("explicit", False),
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


def save_shows(client: SpotifyClient, show_ids: List[str]) -> Dict[str, Any]:
    """
    Save (follow) one or more shows to the user's library.
    
    Args:
        show_ids: List of show IDs or URIs to save (up to 50)
    
    Returns:
        Success message with count of saved shows
    """
    if not show_ids:
        raise ValueError("show_ids cannot be empty")
    
    if len(show_ids) > 50:
        raise ValueError("Cannot save more than 50 shows at once")
    
    # Extract IDs from URIs if needed
    show_ids = [s.split(":")[-1] if ":" in s else s for s in show_ids]
    
    client.current_user_saved_shows_add(show_ids=show_ids)
    
    return {
        "success": True,
        "message": f"Successfully saved {len(show_ids)} show(s)",
        "show_count": len(show_ids),
        "show_ids": show_ids
    }


def remove_saved_shows(client: SpotifyClient, show_ids: List[str]) -> Dict[str, Any]:
    """
    Remove (unfollow) one or more shows from the user's library.
    
    Args:
        show_ids: List of show IDs or URIs to remove (up to 50)
    
    Returns:
        Success message with count of removed shows
    """
    if not show_ids:
        raise ValueError("show_ids cannot be empty")
    
    if len(show_ids) > 50:
        raise ValueError("Cannot remove more than 50 shows at once")
    
    # Extract IDs from URIs if needed
    show_ids = [s.split(":")[-1] if ":" in s else s for s in show_ids]
    
    client.current_user_saved_shows_delete(show_ids=show_ids)
    
    return {
        "success": True,
        "message": f"Successfully removed {len(show_ids)} show(s)",
        "show_count": len(show_ids),
        "show_ids": show_ids
    }


def check_saved_shows(client: SpotifyClient, show_ids: List[str]) -> Dict[str, Any]:
    """
    Check if one or more shows are saved in the user's library.
    
    Args:
        show_ids: List of show IDs or URIs to check (up to 50)
    
    Returns:
        List indicating which shows are saved
    """
    if not show_ids:
        raise ValueError("show_ids cannot be empty")
    
    if len(show_ids) > 50:
        raise ValueError("Cannot check more than 50 shows at once")
    
    # Extract IDs from URIs if needed
    show_ids = [s.split(":")[-1] if ":" in s else s for s in show_ids]
    
    results = client.current_user_saved_shows_contains(show_ids)
    
    return {
        "success": True,
        "shows": [
            {
                "show_id": show_id,
                "is_saved": is_saved
            }
            for show_id, is_saved in zip(show_ids, results)
        ],
        "total_checked": len(show_ids),
        "total_saved": sum(results)
    }


# Tool definitions for MCP
SHOW_TOOLS = [
    {
        "name": "get_show",
        "description": "Get detailed information about a show (podcast) including description, publisher, and episode count.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "show_id": {
                    "type": "string",
                    "description": "Show ID or URI (e.g., 'spotify:show:xxx' or 'showid')"
                },
                "market": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB')"
                }
            },
            "required": ["show_id"]
        }
    },
    {
        "name": "get_several_shows",
        "description": "Get detailed information about multiple shows (podcasts) at once.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "show_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of show IDs or URIs (e.g., ['spotify:show:xxx']). Maximum 50 shows.",
                    "minItems": 1,
                    "maxItems": 50
                },
                "market": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code"
                }
            },
            "required": ["show_ids"]
        }
    },
    {
        "name": "get_show_episodes",
        "description": "Get all episodes from a show (podcast) with pagination support.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "show_id": {
                    "type": "string",
                    "description": "Show ID or URI"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of episodes to return (1-50)",
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
                "market": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code"
                }
            },
            "required": ["show_id"]
        }
    },
    {
        "name": "get_saved_shows",
        "description": "Get the user's saved (followed) shows from their library.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of shows to return (1-50)",
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
        "name": "save_shows",
        "description": "Save (follow) one or more shows to the user's library.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "show_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of show IDs or URIs to save. Maximum 50 shows.",
                    "minItems": 1,
                    "maxItems": 50
                }
            },
            "required": ["show_ids"]
        }
    },
    {
        "name": "remove_saved_shows",
        "description": "Remove (unfollow) one or more shows from the user's library.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "show_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of show IDs or URIs to remove. Maximum 50 shows.",
                    "minItems": 1,
                    "maxItems": 50
                }
            },
            "required": ["show_ids"]
        }
    },
    {
        "name": "check_saved_shows",
        "description": "Check if one or more shows are saved in the user's library.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "show_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of show IDs or URIs to check. Maximum 50 shows.",
                    "minItems": 1,
                    "maxItems": 50
                }
            },
            "required": ["show_ids"]
        }
    }
]
