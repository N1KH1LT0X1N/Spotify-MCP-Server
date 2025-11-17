"""Audiobook management tools for Spotify."""

from typing import List, Dict, Any, Optional
from spotify_mcp.spotify_client import SpotifyClient


def get_audiobook(client: SpotifyClient, audiobook_id: str, market: str = "US") -> Dict[str, Any]:
    """
    Get Spotify catalog information for a single audiobook.
    
    Args:
        audiobook_id: The Spotify ID or URI for the audiobook
        market: ISO 3166-1 alpha-2 country code (e.g., "US", "GB", "CA")
    
    Returns:
        Audiobook details including chapters, authors, narrators, and metadata
    """
    # Extract ID from URI if needed
    audiobook_id = audiobook_id.split(":")[-1] if ":" in audiobook_id else audiobook_id
    
    audiobook = client.audiobook(audiobook_id, market=market)
    
    return {
        "id": audiobook["id"],
        "uri": audiobook["uri"],
        "name": audiobook["name"],
        "authors": [
            {"name": a["name"]} for a in audiobook.get("authors", [])
        ],
        "narrators": [
            {"name": n["name"]} for n in audiobook.get("narrators", [])
        ],
        "publisher": audiobook.get("publisher"),
        "description": audiobook.get("description"),
        "edition": audiobook.get("edition"),
        "language": audiobook.get("language"),
        "total_chapters": audiobook.get("total_chapters", 0),
        "images": audiobook.get("images", []),
        "external_urls": audiobook.get("external_urls", {}),
        "chapters": [
            {
                "id": chapter["id"],
                "name": chapter["name"],
                "uri": chapter["uri"],
                "chapter_number": chapter.get("chapter_number"),
                "duration_ms": chapter.get("duration_ms"),
                "description": chapter.get("description"),
                "release_date": chapter.get("release_date")
            }
            for chapter in audiobook.get("chapters", {}).get("items", [])
        ]
    }


def get_several_audiobooks(client: SpotifyClient, audiobook_ids: List[str], 
                           market: str = "US") -> Dict[str, Any]:
    """
    Get Spotify catalog information for multiple audiobooks.
    
    Args:
        audiobook_ids: List of Spotify IDs or URIs for the audiobooks (max 50)
        market: ISO 3166-1 alpha-2 country code (e.g., "US", "GB", "CA")
    
    Returns:
        List of audiobook details
    """
    if not audiobook_ids:
        raise ValueError("audiobook_ids cannot be empty")
    
    if len(audiobook_ids) > 50:
        raise ValueError("Cannot request more than 50 audiobooks at once")
    
    # Extract IDs from URIs if needed
    audiobook_ids = [aid.split(":")[-1] if ":" in aid else aid for aid in audiobook_ids]
    
    results = client.audiobooks(audiobook_ids, market=market)
    audiobooks = results.get("audiobooks", [])
    
    return {
        "audiobooks": [
            {
                "id": ab["id"],
                "uri": ab["uri"],
                "name": ab["name"],
                "authors": [{"name": a["name"]} for a in ab.get("authors", [])],
                "narrators": [{"name": n["name"]} for n in ab.get("narrators", [])],
                "publisher": ab.get("publisher"),
                "language": ab.get("language"),
                "total_chapters": ab.get("total_chapters", 0),
                "images": ab.get("images", []),
                "external_urls": ab.get("external_urls", {})
            }
            for ab in audiobooks if ab is not None
        ],
        "total": len(audiobooks)
    }


def get_audiobook_chapters(client: SpotifyClient, audiobook_id: str, 
                          limit: int = 20, offset: int = 0, 
                          market: str = "US") -> Dict[str, Any]:
    """
    Get Spotify catalog information about an audiobook's chapters.
    
    Args:
        audiobook_id: The Spotify ID or URI for the audiobook
        limit: Maximum number of chapters to return (1-50, default 20)
        offset: Offset for pagination (default 0)
        market: ISO 3166-1 alpha-2 country code (e.g., "US", "GB", "CA")
    
    Returns:
        List of chapters with metadata
    """
    # Extract ID from URI if needed
    audiobook_id = audiobook_id.split(":")[-1] if ":" in audiobook_id else audiobook_id
    
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    results = client.audiobook_chapters(audiobook_id, limit=limit, offset=offset, market=market)
    
    items = results.get("items", [])
    total = results.get("total", 0)
    
    return {
        "audiobook_id": audiobook_id,
        "chapters": [
            {
                "id": chapter["id"],
                "uri": chapter["uri"],
                "name": chapter["name"],
                "chapter_number": chapter.get("chapter_number"),
                "duration_ms": chapter.get("duration_ms"),
                "description": chapter.get("description"),
                "release_date": chapter.get("release_date"),
                "images": chapter.get("images", []),
                "external_urls": chapter.get("external_urls", {}),
                "resume_point": chapter.get("resume_point")
            }
            for chapter in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


def get_saved_audiobooks(client: SpotifyClient, limit: int = 20, 
                        offset: int = 0) -> Dict[str, Any]:
    """
    Get a list of the audiobooks saved in the current user's library.
    
    Args:
        limit: Maximum number of audiobooks to return (1-50, default 20)
        offset: Offset for pagination (default 0)
    
    Returns:
        List of saved audiobooks with metadata
    """
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    results = client.current_user_saved_audiobooks(limit=limit, offset=offset)
    
    items = results.get("items", [])
    total = results.get("total", 0)
    
    return {
        "audiobooks": [
            {
                "id": item["id"],
                "uri": item["uri"],
                "name": item["name"],
                "authors": [{"name": a["name"]} for a in item.get("authors", [])],
                "narrators": [{"name": n["name"]} for n in item.get("narrators", [])],
                "publisher": item.get("publisher"),
                "language": item.get("language"),
                "total_chapters": item.get("total_chapters", 0),
                "images": item.get("images", []),
                "external_urls": item.get("external_urls", {})
            }
            for item in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


def save_audiobooks(client: SpotifyClient, audiobook_ids: List[str]) -> Dict[str, Any]:
    """
    Save one or more audiobooks to the current user's library.
    
    Args:
        audiobook_ids: List of Spotify IDs or URIs for the audiobooks (max 50)
    
    Returns:
        Success message with count of audiobooks saved
    """
    if not audiobook_ids:
        raise ValueError("audiobook_ids cannot be empty")
    
    if len(audiobook_ids) > 50:
        raise ValueError("Cannot save more than 50 audiobooks at once")
    
    # Extract IDs from URIs if needed
    audiobook_ids = [aid.split(":")[-1] if ":" in aid else aid for aid in audiobook_ids]
    
    client.current_user_saved_audiobooks_add(audiobook_ids)
    
    return {
        "success": True,
        "message": f"Successfully saved {len(audiobook_ids)} audiobook(s) to your library",
        "count": len(audiobook_ids),
        "audiobook_ids": audiobook_ids
    }


def remove_saved_audiobooks(client: SpotifyClient, audiobook_ids: List[str]) -> Dict[str, Any]:
    """
    Remove one or more audiobooks from the current user's library.
    
    Args:
        audiobook_ids: List of Spotify IDs or URIs for the audiobooks (max 50)
    
    Returns:
        Success message with count of audiobooks removed
    """
    if not audiobook_ids:
        raise ValueError("audiobook_ids cannot be empty")
    
    if len(audiobook_ids) > 50:
        raise ValueError("Cannot remove more than 50 audiobooks at once")
    
    # Extract IDs from URIs if needed
    audiobook_ids = [aid.split(":")[-1] if ":" in aid else aid for aid in audiobook_ids]
    
    client.current_user_saved_audiobooks_delete(audiobook_ids)
    
    return {
        "success": True,
        "message": f"Successfully removed {len(audiobook_ids)} audiobook(s) from your library",
        "count": len(audiobook_ids),
        "audiobook_ids": audiobook_ids
    }


def check_saved_audiobooks(client: SpotifyClient, audiobook_ids: List[str]) -> Dict[str, Any]:
    """
    Check if one or more audiobooks are saved in the current user's library.
    
    Args:
        audiobook_ids: List of Spotify IDs or URIs for the audiobooks (max 50)
    
    Returns:
        Dictionary mapping audiobook IDs to whether they are saved
    """
    if not audiobook_ids:
        raise ValueError("audiobook_ids cannot be empty")
    
    if len(audiobook_ids) > 50:
        raise ValueError("Cannot check more than 50 audiobooks at once")
    
    # Extract IDs from URIs if needed
    clean_ids = [aid.split(":")[-1] if ":" in aid else aid for aid in audiobook_ids]
    
    results = client.current_user_saved_audiobooks_contains(clean_ids)
    
    # Create a mapping of ID to saved status
    saved_status = {}
    for original_id, clean_id, is_saved in zip(audiobook_ids, clean_ids, results):
        saved_status[original_id] = is_saved
    
    return {
        "audiobooks": saved_status,
        "total_checked": len(audiobook_ids),
        "saved_count": sum(results)
    }


# Tool definitions for MCP
AUDIOBOOK_TOOLS = [
    {
        "name": "get_audiobook",
        "description": "Get detailed information about a single audiobook including chapters, authors, narrators, and metadata.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "audiobook_id": {
                    "type": "string",
                    "description": "The Spotify ID or URI for the audiobook"
                },
                "market": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB', 'CA')",
                    "default": "US"
                }
            },
            "required": ["audiobook_id"]
        }
    },
    {
        "name": "get_several_audiobooks",
        "description": "Get information about multiple audiobooks in a single request (up to 50 audiobooks).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "audiobook_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of Spotify IDs or URIs for the audiobooks (max 50)",
                    "minItems": 1,
                    "maxItems": 50
                },
                "market": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB', 'CA')",
                    "default": "US"
                }
            },
            "required": ["audiobook_ids"]
        }
    },
    {
        "name": "get_audiobook_chapters",
        "description": "Get information about the chapters of an audiobook with pagination support.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "audiobook_id": {
                    "type": "string",
                    "description": "The Spotify ID or URI for the audiobook"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of chapters (1-50)",
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
                    "description": "ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB', 'CA')",
                    "default": "US"
                }
            },
            "required": ["audiobook_id"]
        }
    },
    {
        "name": "get_saved_audiobooks",
        "description": "Get a list of audiobooks saved in the current user's library.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of audiobooks (1-50)",
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
        "name": "save_audiobooks",
        "description": "Save one or more audiobooks to the current user's library (batch operation, max 50).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "audiobook_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of Spotify IDs or URIs for the audiobooks to save (max 50)",
                    "minItems": 1,
                    "maxItems": 50
                }
            },
            "required": ["audiobook_ids"]
        }
    },
    {
        "name": "remove_saved_audiobooks",
        "description": "Remove one or more audiobooks from the current user's library (batch operation, max 50).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "audiobook_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of Spotify IDs or URIs for the audiobooks to remove (max 50)",
                    "minItems": 1,
                    "maxItems": 50
                }
            },
            "required": ["audiobook_ids"]
        }
    },
    {
        "name": "check_saved_audiobooks",
        "description": "Check if one or more audiobooks are saved in the current user's library.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "audiobook_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of Spotify IDs or URIs for the audiobooks to check (max 50)",
                    "minItems": 1,
                    "maxItems": 50
                }
            },
            "required": ["audiobook_ids"]
        }
    }
]
