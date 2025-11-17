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


def get_user_profile(client: SpotifyClient, user_id: str) -> Dict[str, Any]:
    """
    Get a user's public profile information.
    
    Args:
        user_id: User ID or URI
    
    Returns:
        User profile including display name, followers, etc.
    """
    # Extract ID from URI if needed
    user_id = user_id.split(":")[-1] if ":" in user_id else user_id
    
    user = client.user(user_id=user_id)
    
    return {
        "success": True,
        "user": {
            "id": user.get("id"),
            "display_name": user.get("display_name"),
            "uri": user.get("uri"),
            "followers": user.get("followers", {}).get("total", 0),
            "external_urls": user.get("external_urls", {}),
            "images": user.get("images", [])
        }
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


def get_followed_artists(client: SpotifyClient, limit: int = 20, 
                        after: str = None) -> Dict[str, Any]:
    """
    Get artists followed by the current user.
    
    Args:
        limit: Maximum number of artists to return (1-50, default 20)
        after: Last artist ID retrieved from previous request (for pagination)
    
    Returns:
        List of followed artists with pagination info
    """
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    
    result = client.current_user_following_artists(limit=limit, after=after)
    
    artists = result.get("artists", {})
    items = artists.get("items", [])
    
    return {
        "success": True,
        "artists": [
            {
                "id": artist.get("id"),
                "uri": artist.get("uri"),
                "name": artist.get("name"),
                "genres": artist.get("genres", []),
                "popularity": artist.get("popularity", 0),
                "followers": artist.get("followers", {}).get("total", 0),
                "images": artist.get("images", [])
            }
            for artist in items
        ],
        "total": artists.get("total", 0),
        "limit": limit,
        "next": artists.get("next"),
        "cursors": artists.get("cursors", {})
    }


def follow_artists_or_users(client: SpotifyClient, ids: list[str], 
                           follow_type: str = "artist") -> Dict[str, Any]:
    """
    Follow one or more artists or users.
    
    Args:
        ids: List of artist or user IDs or URIs (up to 50)
        follow_type: Type to follow - "artist" or "user"
    
    Returns:
        Success message
    """
    if not ids:
        raise ValueError("ids cannot be empty")
    
    if len(ids) > 50:
        raise ValueError("Cannot follow more than 50 artists/users at once")
    
    valid_types = ["artist", "user"]
    if follow_type not in valid_types:
        raise ValueError(f"follow_type must be one of: {', '.join(valid_types)}")
    
    # Extract IDs from URIs if needed
    ids = [id.split(":")[-1] if ":" in id else id for id in ids]
    
    if follow_type == "artist":
        client.user_follow_artists(ids=ids)
    else:
        client.user_follow_users(ids=ids)
    
    return {
        "success": True,
        "message": f"Successfully followed {len(ids)} {follow_type}(s)",
        "count": len(ids),
        "type": follow_type,
        "ids": ids
    }


def unfollow_artists_or_users(client: SpotifyClient, ids: list[str], 
                              follow_type: str = "artist") -> Dict[str, Any]:
    """
    Unfollow one or more artists or users.
    
    Args:
        ids: List of artist or user IDs or URIs (up to 50)
        follow_type: Type to unfollow - "artist" or "user"
    
    Returns:
        Success message
    """
    if not ids:
        raise ValueError("ids cannot be empty")
    
    if len(ids) > 50:
        raise ValueError("Cannot unfollow more than 50 artists/users at once")
    
    valid_types = ["artist", "user"]
    if follow_type not in valid_types:
        raise ValueError(f"follow_type must be one of: {', '.join(valid_types)}")
    
    # Extract IDs from URIs if needed
    ids = [id.split(":")[-1] if ":" in id else id for id in ids]
    
    if follow_type == "artist":
        client.user_unfollow_artists(ids=ids)
    else:
        client.user_unfollow_users(ids=ids)
    
    return {
        "success": True,
        "message": f"Successfully unfollowed {len(ids)} {follow_type}(s)",
        "count": len(ids),
        "type": follow_type,
        "ids": ids
    }


def check_following_artists_or_users(client: SpotifyClient, ids: list[str], 
                                     follow_type: str = "artist") -> Dict[str, Any]:
    """
    Check if current user follows artists or users.
    
    Args:
        ids: List of artist or user IDs or URIs (up to 50)
        follow_type: Type to check - "artist" or "user"
    
    Returns:
        List indicating which artists/users are followed
    """
    if not ids:
        raise ValueError("ids cannot be empty")
    
    if len(ids) > 50:
        raise ValueError("Cannot check more than 50 artists/users at once")
    
    valid_types = ["artist", "user"]
    if follow_type not in valid_types:
        raise ValueError(f"follow_type must be one of: {', '.join(valid_types)}")
    
    # Extract IDs from URIs if needed
    ids = [id.split(":")[-1] if ":" in id else id for id in ids]
    
    results = client.current_user_following_contains(ids=ids, follow_type=follow_type)
    
    return {
        "success": True,
        "type": follow_type,
        "following": [
            {
                "id": id,
                "is_following": is_following
            }
            for id, is_following in zip(ids, results)
        ],
        "total_checked": len(ids),
        "total_following": sum(results)
    }


def check_current_user_follows_playlist(client: SpotifyClient, playlist_id: str, 
                                       user_ids: list[str] = None) -> Dict[str, Any]:
    """
    Check if current user (or other users) follow a playlist.
    
    Args:
        playlist_id: Playlist ID or URI
        user_ids: List of user IDs to check (if empty, checks current user)
    
    Returns:
        List indicating which users follow the playlist
    """
    # Extract ID from URI if needed
    playlist_id = playlist_id.split(":")[-1] if ":" in playlist_id else playlist_id
    
    # If no user_ids provided, get current user's ID
    if not user_ids:
        current = client.current_user()
        user_ids = [current.get("id")]
    else:
        # Extract IDs from URIs if needed
        user_ids = [id.split(":")[-1] if ":" in id else id for id in user_ids]
    
    if len(user_ids) > 5:
        raise ValueError("Cannot check more than 5 users at once")
    
    results = client.playlist_is_following(playlist_id=playlist_id, user_ids=user_ids)
    
    return {
        "success": True,
        "playlist_id": playlist_id,
        "users": [
            {
                "user_id": user_id,
                "is_following": is_following
            }
            for user_id, is_following in zip(user_ids, results)
        ],
        "total_checked": len(user_ids),
        "total_following": sum(results)
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
    },
    {
        "name": "get_user_profile",
        "description": "Get a user's public profile information by user ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID or URI (e.g., 'spotify:user:xxx' or 'userid')"
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "get_followed_artists",
        "description": "Get artists followed by the current user.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of artists to return (1-50)",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 20
                },
                "after": {
                    "type": "string",
                    "description": "Last artist ID from previous request (for pagination)"
                }
            }
        }
    },
    {
        "name": "follow_artists_or_users",
        "description": "Follow one or more artists or users.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of artist or user IDs or URIs to follow. Maximum 50.",
                    "minItems": 1,
                    "maxItems": 50
                },
                "follow_type": {
                    "type": "string",
                    "enum": ["artist", "user"],
                    "description": "Type to follow - 'artist' or 'user'",
                    "default": "artist"
                }
            },
            "required": ["ids"]
        }
    },
    {
        "name": "unfollow_artists_or_users",
        "description": "Unfollow one or more artists or users.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of artist or user IDs or URIs to unfollow. Maximum 50.",
                    "minItems": 1,
                    "maxItems": 50
                },
                "follow_type": {
                    "type": "string",
                    "enum": ["artist", "user"],
                    "description": "Type to unfollow - 'artist' or 'user'",
                    "default": "artist"
                }
            },
            "required": ["ids"]
        }
    },
    {
        "name": "check_following_artists_or_users",
        "description": "Check if current user follows one or more artists or users.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of artist or user IDs or URIs to check. Maximum 50.",
                    "minItems": 1,
                    "maxItems": 50
                },
                "follow_type": {
                    "type": "string",
                    "enum": ["artist", "user"],
                    "description": "Type to check - 'artist' or 'user'",
                    "default": "artist"
                }
            },
            "required": ["ids"]
        }
    },
    {
        "name": "check_current_user_follows_playlist",
        "description": "Check if current user (or other users) follow a playlist.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "playlist_id": {
                    "type": "string",
                    "description": "Playlist ID or URI"
                },
                "user_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of user IDs to check (if empty, checks current user). Maximum 5.",
                    "maxItems": 5
                }
            },
            "required": ["playlist_id"]
        }
    }
]
