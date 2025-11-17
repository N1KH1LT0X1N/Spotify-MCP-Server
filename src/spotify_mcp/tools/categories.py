"""
Browse category tools for Spotify MCP server.
Provides access to Spotify's browse categories for content discovery.
"""

from typing import Dict, Any
from spotify_mcp.spotify_client import SpotifyClient


def get_several_browse_categories(client: SpotifyClient, country: str = None, 
                                  locale: str = None, limit: int = 20, 
                                  offset: int = 0) -> Dict[str, Any]:
    """
    Get a list of categories used to tag items in Spotify.
    
    Args:
        country: ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB')
        locale: Desired language (e.g., 'en_US', 'es_MX')
        limit: Maximum number of categories to return (1-50, default 20)
        offset: Index of first category to return (default 0)
    
    Returns:
        Dictionary containing categories with pagination info
    """
    if limit < 1 or limit > 50:
        raise ValueError("Limit must be between 1 and 50")
    
    result = client.categories(country=country, locale=locale, limit=limit, offset=offset)
    
    categories = []
    for cat in result.get("categories", {}).get("items", []):
        categories.append({
            "id": cat.get("id"),
            "name": cat.get("name"),
            "href": cat.get("href"),
            "icons": [{"url": icon.get("url"), "width": icon.get("width"), 
                      "height": icon.get("height")} for icon in cat.get("icons", [])]
        })
    
    return {
        "categories": categories,
        "total": result.get("categories", {}).get("total", 0),
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < result.get("categories", {}).get("total", 0)
    }


def get_single_browse_category(client: SpotifyClient, category_id: str,
                               country: str = None, locale: str = None) -> Dict[str, Any]:
    """
    Get a single category used to tag items in Spotify.
    
    Args:
        category_id: The Spotify category ID
        country: ISO 3166-1 alpha-2 country code
        locale: Desired language
    
    Returns:
        Dictionary containing category information
    """
    if not category_id:
        raise ValueError("category_id is required")
    
    result = client.category(category_id, country=country, locale=locale)
    
    return {
        "id": result.get("id"),
        "name": result.get("name"),
        "href": result.get("href"),
        "icons": [{"url": icon.get("url"), "width": icon.get("width"), 
                  "height": icon.get("height")} for icon in result.get("icons", [])]
    }


# MCP Tool Definitions
CATEGORY_TOOLS = [
    {
        "name": "get_several_browse_categories",
        "description": "Get a list of Spotify browse categories for content discovery and tagging",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB'). Provides country-specific categories."
                },
                "locale": {
                    "type": "string",
                    "description": "Desired language for category names (e.g., 'en_US', 'es_MX')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of categories to return (1-50)",
                    "default": 20
                },
                "offset": {
                    "type": "integer",
                    "description": "Index of first category to return for pagination",
                    "default": 0
                }
            }
        }
    },
    {
        "name": "get_single_browse_category",
        "description": "Get detailed information about a specific Spotify browse category",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category_id": {
                    "type": "string",
                    "description": "The Spotify category ID (e.g., 'toplists', 'mood', 'party')"
                },
                "country": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code for country-specific info"
                },
                "locale": {
                    "type": "string",
                    "description": "Desired language for category name"
                }
            },
            "required": ["category_id"]
        }
    }
]
