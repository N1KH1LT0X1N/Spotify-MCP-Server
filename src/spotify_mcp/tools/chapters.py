"""
Chapter tools for Spotify MCP server.
Provides access to audiobook chapter information.
"""

from typing import Dict, Any, List
from spotify_mcp.spotify_client import SpotifyClient


def get_chapter(client: SpotifyClient, chapter_id: str, market: str = None) -> Dict[str, Any]:
    """
    Get detailed information about a specific audiobook chapter.
    
    Args:
        chapter_id: The Spotify chapter ID or URI
        market: ISO 3166-1 alpha-2 country code (e.g., 'US')
    
    Returns:
        Dictionary containing chapter details
    """
    if not chapter_id:
        raise ValueError("chapter_id is required")
    
    # Extract ID from URI if needed
    chapter_id = chapter_id.split(":")[-1] if ":" in chapter_id else chapter_id
    
    result = client.chapter(chapter_id, market=market)
    
    return {
        "id": result.get("id"),
        "name": result.get("name"),
        "description": result.get("description"),
        "chapter_number": result.get("chapter_number"),
        "duration_ms": result.get("duration_ms"),
        "explicit": result.get("explicit"),
        "release_date": result.get("release_date"),
        "release_date_precision": result.get("release_date_precision"),
        "resume_point": result.get("resume_point"),
        "audiobook": {
            "id": result.get("audiobook", {}).get("id"),
            "name": result.get("audiobook", {}).get("name"),
            "authors": [{"name": a.get("name")} for a in result.get("audiobook", {}).get("authors", [])]
        },
        "audio_preview_url": result.get("audio_preview_url"),
        "languages": result.get("languages", []),
        "available_markets": result.get("available_markets", [])
    }


def get_several_chapters(client: SpotifyClient, chapter_ids: List[str], 
                        market: str = None) -> Dict[str, Any]:
    """
    Get information about multiple chapters efficiently (batch request).
    
    Args:
        chapter_ids: List of Spotify chapter IDs or URIs (max 50)
        market: ISO 3166-1 alpha-2 country code
    
    Returns:
        Dictionary containing list of chapters
    """
    if not chapter_ids:
        raise ValueError("chapter_ids list cannot be empty")
    
    if len(chapter_ids) > 50:
        raise ValueError("Maximum 50 chapters per request")
    
    # Extract IDs from URIs
    ids = [cid.split(":")[-1] if ":" in cid else cid for cid in chapter_ids]
    
    result = client.chapters(ids, market=market)
    
    chapters = []
    for chapter in result.get("chapters", []):
        if chapter:  # Some may be None if not found
            chapters.append({
                "id": chapter.get("id"),
                "name": chapter.get("name"),
                "description": chapter.get("description"),
                "chapter_number": chapter.get("chapter_number"),
                "duration_ms": chapter.get("duration_ms"),
                "explicit": chapter.get("explicit"),
                "audiobook": {
                    "id": chapter.get("audiobook", {}).get("id"),
                    "name": chapter.get("audiobook", {}).get("name")
                },
                "audio_preview_url": chapter.get("audio_preview_url")
            })
    
    return {
        "chapters": chapters,
        "total": len(chapters)
    }


# MCP Tool Definitions
CHAPTER_TOOLS = [
    {
        "name": "get_chapter",
        "description": "Get detailed information about a specific audiobook chapter including duration, chapter number, and preview",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chapter_id": {
                    "type": "string",
                    "description": "Spotify chapter ID or URI (e.g., 'spotify:chapter:xxx' or just the ID)"
                },
                "market": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB') for market-specific content"
                }
            },
            "required": ["chapter_id"]
        }
    },
    {
        "name": "get_several_chapters",
        "description": "Get information about multiple audiobook chapters efficiently in a single batch request (max 50)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chapter_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of chapter IDs or URIs (e.g., ['spotify:chapter:xxx', 'chapterid2']). Maximum 50 chapters."
                },
                "market": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code for market availability"
                }
            },
            "required": ["chapter_ids"]
        }
    }
]
