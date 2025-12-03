"""
Episode tools for Spotify MCP server.
Provides access to podcast episodes and saved episode management.
"""

from typing import Dict, Any, List
from spotify_mcp.spotify_client import SpotifyClient


def get_episode(client: SpotifyClient, episode_id: str, market: str = None) -> Dict[str, Any]:
    """
    Get detailed information about a podcast episode.
    
    Args:
        episode_id: The Spotify episode ID or URI
        market: ISO 3166-1 alpha-2 country code
    
    Returns:
        Dictionary containing episode details
    """
    if not episode_id:
        raise ValueError("episode_id is required")
    
    # Extract ID from URI if needed
    episode_id = episode_id.split(":")[-1] if ":" in episode_id else episode_id
    
    result = client.episode(episode_id, market)
    
    return {
        "id": result.get("id"),
        "name": result.get("name"),
        "description": result.get("description"),
        "duration_ms": result.get("duration_ms"),
        "explicit": result.get("explicit"),
        "release_date": result.get("release_date"),
        "release_date_precision": result.get("release_date_precision"),
        "resume_point": result.get("resume_point"),
        "show": {
            "id": result.get("show", {}).get("id"),
            "name": result.get("show", {}).get("name"),
            "publisher": result.get("show", {}).get("publisher")
        },
        "audio_preview_url": result.get("audio_preview_url"),
        "images": [{"url": img.get("url"), "width": img.get("width"), 
                   "height": img.get("height")} for img in result.get("images", [])],
        "languages": result.get("languages", []),
        "is_playable": result.get("is_playable")
    }


def get_several_episodes(client: SpotifyClient, episode_ids: List[str], 
                        market: str = None) -> Dict[str, Any]:
    """
    Get information about multiple episodes efficiently (batch request).
    
    Args:
        episode_ids: List of Spotify episode IDs or URIs (max 50)
        market: ISO 3166-1 alpha-2 country code
    
    Returns:
        Dictionary containing list of episodes
    """
    if not episode_ids:
        raise ValueError("episode_ids list cannot be empty")
    
    if len(episode_ids) > 50:
        raise ValueError("Maximum 50 episodes per request")
    
    # Extract IDs from URIs
    ids = [eid.split(":")[-1] if ":" in eid else eid for eid in episode_ids]
    
    result = client.episodes(ids, market)
    
    episodes = []
    for episode in result.get("episodes", []):
        if episode:
            episodes.append({
                "id": episode.get("id"),
                "name": episode.get("name"),
                "description": episode.get("description"),
                "duration_ms": episode.get("duration_ms"),
                "release_date": episode.get("release_date"),
                "show": {
                    "id": episode.get("show", {}).get("id"),
                    "name": episode.get("show", {}).get("name")
                },
                "audio_preview_url": episode.get("audio_preview_url")
            })
    
    return {
        "episodes": episodes,
        "total": len(episodes)
    }


def get_saved_episodes(client: SpotifyClient, market: str = None, 
                      limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    Get user's saved podcast episodes.
    
    Args:
        market: ISO 3166-1 alpha-2 country code
        limit: Maximum number of episodes (1-50, default 20)
        offset: Index of first episode (default 0)
    
    Returns:
        Dictionary containing saved episodes with pagination
    """
    if limit < 1 or limit > 50:
        raise ValueError("Limit must be between 1 and 50")
    
    result = client.current_user_saved_episodes(limit=limit, offset=offset, market=market)
    
    episodes = []
    for item in result.get("items", []):
        episode = item.get("episode", {})
        episodes.append({
            "id": episode.get("id"),
            "name": episode.get("name"),
            "description": episode.get("description"),
            "duration_ms": episode.get("duration_ms"),
            "release_date": episode.get("release_date"),
            "show": {
                "id": episode.get("show", {}).get("id"),
                "name": episode.get("show", {}).get("name")
            },
            "added_at": item.get("added_at")
        })
    
    return {
        "episodes": episodes,
        "total": result.get("total", 0),
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < result.get("total", 0)
    }


def save_episodes(client: SpotifyClient, episode_ids: List[str]) -> Dict[str, Any]:
    """
    Save one or more episodes to user's library.
    
    Args:
        episode_ids: List of episode IDs or URIs to save (max 50)
    
    Returns:
        Success confirmation
    """
    if not episode_ids:
        raise ValueError("episode_ids list cannot be empty")
    
    if len(episode_ids) > 50:
        raise ValueError("Maximum 50 episodes per request")
    
    # Extract IDs from URIs
    ids = [eid.split(":")[-1] if ":" in eid else eid for eid in episode_ids]
    
    client.current_user_saved_episodes_add(ids)
    
    return {
        "success": True,
        "saved_count": len(ids),
        "message": f"Successfully saved {len(ids)} episode(s) to your library"
    }


def remove_saved_episodes(client: SpotifyClient, episode_ids: List[str]) -> Dict[str, Any]:
    """
    Remove one or more episodes from user's library.
    
    Args:
        episode_ids: List of episode IDs or URIs to remove (max 50)
    
    Returns:
        Success confirmation
    """
    if not episode_ids:
        raise ValueError("episode_ids list cannot be empty")
    
    if len(episode_ids) > 50:
        raise ValueError("Maximum 50 episodes per request")
    
    # Extract IDs from URIs
    ids = [eid.split(":")[-1] if ":" in eid else eid for eid in episode_ids]
    
    client.current_user_saved_episodes_delete(ids)
    
    return {
        "success": True,
        "removed_count": len(ids),
        "message": f"Successfully removed {len(ids)} episode(s) from your library"
    }


def check_saved_episodes(client: SpotifyClient, episode_ids: List[str]) -> Dict[str, Any]:
    """
    Check if one or more episodes are in user's library.
    
    Args:
        episode_ids: List of episode IDs or URIs to check (max 50)
    
    Returns:
        Dictionary with boolean array indicating saved status
    """
    if not episode_ids:
        raise ValueError("episode_ids list cannot be empty")
    
    if len(episode_ids) > 50:
        raise ValueError("Maximum 50 episodes per request")
    
    # Extract IDs from URIs
    ids = [eid.split(":")[-1] if ":" in eid else eid for eid in episode_ids]
    
    result = client.current_user_saved_episodes_contains(ids)
    
    return {
        "results": [{"episode_id": ids[i], "is_saved": result[i]} 
                   for i in range(len(ids))],
        "total_checked": len(ids),
        "saved_count": sum(result)
    }


# MCP Tool Definitions
EPISODE_TOOLS = [
    {
        "name": "get_episode",
        "description": "Get detailed information about a podcast episode including duration, show info, and playback status",
        "inputSchema": {
            "type": "object",
            "properties": {
                "episode_id": {
                    "type": "string",
                    "description": "Spotify episode ID or URI (e.g., 'spotify:episode:xxx' or just the ID)"
                },
                "market": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code for market-specific content"
                }
            },
            "required": ["episode_id"]
        }
    },
    {
        "name": "get_several_episodes",
        "description": "Get information about multiple podcast episodes efficiently in a single batch request (max 50)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "episode_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of episode IDs or URIs (max 50)"
                },
                "market": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code"
                }
            },
            "required": ["episode_ids"]
        }
    },
    {
        "name": "get_saved_episodes",
        "description": "Get user's saved podcast episodes from their library with pagination support",
        "inputSchema": {
            "type": "object",
            "properties": {
                "market": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of episodes to return (1-50)",
                    "default": 20
                },
                "offset": {
                    "type": "integer",
                    "description": "Index of first episode for pagination",
                    "default": 0
                }
            }
        }
    },
    {
        "name": "save_episodes",
        "description": "Save one or more podcast episodes to user's library for later listening (max 50 per request)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "episode_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of episode IDs or URIs to save (max 50)"
                }
            },
            "required": ["episode_ids"]
        }
    },
    {
        "name": "remove_saved_episodes",
        "description": "Remove one or more podcast episodes from user's library (max 50 per request)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "episode_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of episode IDs or URIs to remove (max 50)"
                }
            },
            "required": ["episode_ids"]
        }
    },
    {
        "name": "check_saved_episodes",
        "description": "Check if one or more podcast episodes are saved in user's library (max 50 per request)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "episode_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of episode IDs or URIs to check (max 50)"
                }
            },
            "required": ["episode_ids"]
        }
    }
]
