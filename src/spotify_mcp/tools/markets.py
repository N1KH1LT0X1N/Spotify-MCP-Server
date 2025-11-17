"""
Market tools for Spotify MCP server.
Provides information about available Spotify markets.
"""

from typing import Dict, Any
from spotify_mcp.spotify_client import SpotifyClient


def get_available_markets(client: SpotifyClient) -> Dict[str, Any]:
    """
    Get the list of markets where Spotify is available.
    
    Returns ISO 3166-1 alpha-2 country codes for all markets where
    Spotify is currently available.
    
    Returns:
        Dictionary containing list of available market codes
    """
    result = client.available_markets()
    
    markets = result.get("markets", [])
    
    return {
        "markets": sorted(markets),  # Sort alphabetically
        "total": len(markets),
        "usage": "Use these ISO 3166-1 alpha-2 country codes (e.g., 'US', 'GB', 'DE') when specifying markets in other API calls"
    }


# MCP Tool Definitions
MARKET_TOOLS = [
    {
        "name": "get_available_markets",
        "description": "Get the list of all markets (countries) where Spotify is available. Returns ISO 3166-1 alpha-2 country codes.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]
