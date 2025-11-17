"""
Genre tools for Spotify MCP server.
Provides access to available genre seeds for recommendations.
"""

from typing import Dict, Any
from spotify_mcp.spotify_client import SpotifyClient


def get_available_genre_seeds(client: SpotifyClient) -> Dict[str, Any]:
    """
    Get the list of available genre seeds for recommendations.
    
    These genres can be used with the get_recommendations tool to find music
    based on genre preferences.
    
    Returns:
        Dictionary containing list of available genres
    """
    result = client.recommendation_genre_seeds()
    
    genres = result.get("genres", [])
    
    return {
        "genres": sorted(genres),  # Sort alphabetically for easier browsing
        "total": len(genres),
        "usage": "Use these genre names with get_recommendations to discover music by genre"
    }


# MCP Tool Definitions
GENRE_TOOLS = [
    {
        "name": "get_available_genre_seeds",
        "description": "Get the list of available genre seeds that can be used with recommendations. Returns all valid genre names for music discovery.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]
