"""Playback control tools for Spotify."""

from typing import Optional, List, Dict, Any
from spotify_mcp.spotify_client import SpotifyClient


def play(client: SpotifyClient, context_uri: Optional[str] = None, 
         uris: Optional[List[str]] = None, device_id: Optional[str] = None,
         offset_position: Optional[int] = None, offset_uri: Optional[str] = None) -> Dict[str, Any]:
    """
    Start or resume playback.
    
    Args:
        context_uri: Spotify URI of album, artist, or playlist (e.g., spotify:album:xxx)
        uris: List of track URIs to play (e.g., ["spotify:track:xxx"])
        device_id: Device ID to play on (optional)
        offset_position: Position in context to start (0-indexed)
        offset_uri: URI of track in context to start from
    
    Returns:
        Success message
    
    Examples:
        - Play a specific track: uris=["spotify:track:6rqhFgbbKwnb9MLmUQDhG6"]
        - Play an album: context_uri="spotify:album:5YnC8iXCc2MXlKqy9YsWdq"
        - Play a playlist: context_uri="spotify:playlist:37i9dQZF1DXcBWIGoYBM5M"
    """
    offset = None
    if offset_position is not None:
        offset = {"position": offset_position}
    elif offset_uri is not None:
        offset = {"uri": offset_uri}
    
    client.start_playback(device_id=device_id, context_uri=context_uri, uris=uris, offset=offset)
    
    return {
        "success": True,
        "message": "Playback started",
        "context": context_uri or "tracks",
        "device_id": device_id or "default device"
    }


def pause(client: SpotifyClient, device_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Pause playback on the user's account.
    
    Args:
        device_id: Device ID to pause (optional)
    
    Returns:
        Success message
    """
    client.pause_playback(device_id=device_id)
    
    return {
        "success": True,
        "message": "Playback paused",
        "device_id": device_id or "default device"
    }


def skip_next(client: SpotifyClient, device_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Skip to the next track in the user's queue.
    
    Args:
        device_id: Device ID (optional)
    
    Returns:
        Success message
    """
    client.next_track(device_id=device_id)
    
    return {
        "success": True,
        "message": "Skipped to next track",
        "device_id": device_id or "default device"
    }


def skip_previous(client: SpotifyClient, device_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Skip to the previous track in the user's queue.
    Note: This will restart the current track if more than 3 seconds have elapsed.
    
    Args:
        device_id: Device ID (optional)
    
    Returns:
        Success message
    """
    client.previous_track(device_id=device_id)
    
    return {
        "success": True,
        "message": "Skipped to previous track",
        "device_id": device_id or "default device"
    }


def get_current_playback(client: SpotifyClient) -> Dict[str, Any]:
    """
    Get information about the user's current playback state.
    
    Returns:
        Current playback information including track, artist, album, progress, 
        device, shuffle state, repeat state, and more.
    """
    playback = client.current_playback()
    
    if not playback:
        return {
            "is_playing": False,
            "message": "No active playback"
        }
    
    track = playback.get("item", {})
    device = playback.get("device", {})
    
    return {
        "is_playing": playback.get("is_playing", False),
        "shuffle_state": playback.get("shuffle_state", False),
        "repeat_state": playback.get("repeat_state", "off"),
        "progress_ms": playback.get("progress_ms", 0),
        "track": {
            "name": track.get("name"),
            "uri": track.get("uri"),
            "id": track.get("id"),
            "duration_ms": track.get("duration_ms"),
            "artists": [{"name": a["name"], "uri": a["uri"]} for a in track.get("artists", [])],
            "album": {
                "name": track.get("album", {}).get("name"),
                "uri": track.get("album", {}).get("uri"),
            }
        },
        "device": {
            "id": device.get("id"),
            "name": device.get("name"),
            "type": device.get("type"),
            "volume_percent": device.get("volume_percent"),
            "is_active": device.get("is_active", False)
        },
        "context": {
            "type": playback.get("context", {}).get("type") if playback.get("context") else None,
            "uri": playback.get("context", {}).get("uri") if playback.get("context") else None,
        }
    }


def get_available_devices(client: SpotifyClient) -> Dict[str, Any]:
    """
    Get a list of available Spotify Connect devices.
    
    Returns:
        List of available devices with their IDs, names, types, and status.
    """
    devices_response = client.devices()
    devices = devices_response.get("devices", [])
    
    return {
        "devices": [
            {
                "id": d.get("id"),
                "name": d.get("name"),
                "type": d.get("type"),
                "is_active": d.get("is_active", False),
                "is_private_session": d.get("is_private_session", False),
                "is_restricted": d.get("is_restricted", False),
                "volume_percent": d.get("volume_percent"),
            }
            for d in devices
        ],
        "total_devices": len(devices)
    }


def transfer_playback(client: SpotifyClient, device_id: str, 
                      force_play: bool = False) -> Dict[str, Any]:
    """
    Transfer playback to a different device.
    
    Args:
        device_id: ID of the device to transfer to
        force_play: If true, playback will start on the new device
    
    Returns:
        Success message
    """
    client.transfer_playback(device_id=device_id, force_play=force_play)
    
    return {
        "success": True,
        "message": f"Playback transferred to device",
        "device_id": device_id,
        "force_play": force_play
    }


def set_volume(client: SpotifyClient, volume_percent: int, 
               device_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Set the volume for the user's current playback device.
    
    Args:
        volume_percent: Volume level (0-100)
        device_id: Device ID (optional)
    
    Returns:
        Success message
    """
    if not 0 <= volume_percent <= 100:
        raise ValueError("Volume must be between 0 and 100")
    
    client.volume(volume_percent=volume_percent, device_id=device_id)
    
    return {
        "success": True,
        "message": f"Volume set to {volume_percent}%",
        "volume_percent": volume_percent,
        "device_id": device_id or "default device"
    }


def set_shuffle(client: SpotifyClient, state: bool, 
                device_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Toggle shuffle mode on or off.
    
    Args:
        state: True to enable shuffle, False to disable
        device_id: Device ID (optional)
    
    Returns:
        Success message
    """
    client.shuffle(state=state, device_id=device_id)
    
    return {
        "success": True,
        "message": f"Shuffle {'enabled' if state else 'disabled'}",
        "shuffle_state": state,
        "device_id": device_id or "default device"
    }


def set_repeat(client: SpotifyClient, state: str, 
               device_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Set repeat mode for playback.
    
    Args:
        state: Repeat mode - "track", "context", or "off"
        device_id: Device ID (optional)
    
    Returns:
        Success message
    """
    valid_states = ["track", "context", "off"]
    if state not in valid_states:
        raise ValueError(f"State must be one of: {', '.join(valid_states)}")
    
    client.repeat(state=state, device_id=device_id)
    
    return {
        "success": True,
        "message": f"Repeat mode set to '{state}'",
        "repeat_state": state,
        "device_id": device_id or "default device"
    }


def seek_to_position(client: SpotifyClient, position_ms: int, 
                    device_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Seek to a specific position in the currently playing track.
    
    Args:
        position_ms: Position in milliseconds
        device_id: Device ID (optional)
    
    Returns:
        Success message
    """
    if position_ms < 0:
        raise ValueError("Position must be non-negative")
    
    client.seek_track(position_ms=position_ms, device_id=device_id)
    
    return {
        "success": True,
        "message": f"Seeked to position {position_ms}ms",
        "position_ms": position_ms,
        "device_id": device_id or "default device"
    }


def get_recently_played(client: SpotifyClient, limit: int = 20, 
                        after: Optional[int] = None, before: Optional[int] = None) -> Dict[str, Any]:
    """
    Get the current user's recently played tracks.
    
    Args:
        limit: Maximum number of items to return (1-50, default 20)
        after: Unix timestamp in milliseconds - returns tracks played after this time
        before: Unix timestamp in milliseconds - returns tracks played before this time
    
    Returns:
        List of recently played tracks with play history context
    
    Note:
        Only one of 'after' or 'before' can be specified at a time.
    """
    if limit < 1 or limit > 50:
        raise ValueError("Limit must be between 1 and 50")
    
    if after is not None and before is not None:
        raise ValueError("Cannot specify both 'after' and 'before' parameters")
    
    response = client.current_user_recently_played(limit=limit, after=after, before=before)
    
    items = response.get("items", [])
    
    return {
        "items": [
            {
                "track": {
                    "name": item["track"]["name"],
                    "uri": item["track"]["uri"],
                    "id": item["track"]["id"],
                    "duration_ms": item["track"]["duration_ms"],
                    "artists": [{"name": a["name"], "uri": a["uri"]} for a in item["track"]["artists"]],
                    "album": {
                        "name": item["track"]["album"]["name"],
                        "uri": item["track"]["album"]["uri"],
                    }
                },
                "played_at": item.get("played_at"),
                "context": {
                    "type": item["context"]["type"] if item.get("context") else None,
                    "uri": item["context"]["uri"] if item.get("context") else None,
                }
            }
            for item in items
        ],
        "total": len(items),
        "cursors": response.get("cursors", {})
    }


# Tool definitions for MCP
PLAYBACK_TOOLS = [
    {
        "name": "play",
        "description": "Start or resume playback. Can play a track, album, artist, or playlist.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "context_uri": {
                    "type": "string",
                    "description": "Spotify URI of album, artist, or playlist (e.g., spotify:album:xxx)"
                },
                "uris": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of track URIs to play (e.g., ['spotify:track:xxx'])"
                },
                "device_id": {
                    "type": "string",
                    "description": "Device ID to play on (optional)"
                },
                "offset_position": {
                    "type": "integer",
                    "description": "Position in context to start (0-indexed)"
                },
                "offset_uri": {
                    "type": "string",
                    "description": "URI of track in context to start from"
                }
            }
        }
    },
    {
        "name": "pause",
        "description": "Pause playback on the user's account.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "Device ID to pause (optional)"
                }
            }
        }
    },
    {
        "name": "skip_next",
        "description": "Skip to the next track in the user's queue.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "Device ID (optional)"
                }
            }
        }
    },
    {
        "name": "skip_previous",
        "description": "Skip to the previous track. Restarts current track if more than 3 seconds have elapsed.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "Device ID (optional)"
                }
            }
        }
    },
    {
        "name": "get_current_playback",
        "description": "Get information about the user's current playback state including track, artist, progress, device info, etc.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_available_devices",
        "description": "Get a list of available Spotify Connect devices.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "transfer_playback",
        "description": "Transfer playback to a different device.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "ID of the device to transfer to"
                },
                "force_play": {
                    "type": "boolean",
                    "description": "If true, playback will start on the new device",
                    "default": False
                }
            },
            "required": ["device_id"]
        }
    },
    {
        "name": "set_volume",
        "description": "Set the volume for the user's current playback device.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "volume_percent": {
                    "type": "integer",
                    "description": "Volume level (0-100)",
                    "minimum": 0,
                    "maximum": 100
                },
                "device_id": {
                    "type": "string",
                    "description": "Device ID (optional)"
                }
            },
            "required": ["volume_percent"]
        }
    },
    {
        "name": "set_shuffle",
        "description": "Toggle shuffle mode on or off.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "state": {
                    "type": "boolean",
                    "description": "True to enable shuffle, False to disable"
                },
                "device_id": {
                    "type": "string",
                    "description": "Device ID (optional)"
                }
            },
            "required": ["state"]
        }
    },
    {
        "name": "set_repeat",
        "description": "Set repeat mode for playback.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "state": {
                    "type": "string",
                    "enum": ["track", "context", "off"],
                    "description": "Repeat mode: 'track' (repeat current track), 'context' (repeat album/playlist), or 'off'"
                },
                "device_id": {
                    "type": "string",
                    "description": "Device ID (optional)"
                }
            },
            "required": ["state"]
        }
    },
    {
        "name": "seek_to_position",
        "description": "Seek to a specific position in the currently playing track.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "position_ms": {
                    "type": "integer",
                    "description": "Position in milliseconds",
                    "minimum": 0
                },
                "device_id": {
                    "type": "string",
                    "description": "Device ID (optional)"
                }
            },
            "required": ["position_ms"]
        }
    },
    {
        "name": "get_recently_played",
        "description": "Get the current user's recently played tracks with timestamps and context.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of items to return (1-50)",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 20
                },
                "after": {
                    "type": "integer",
                    "description": "Unix timestamp in milliseconds - returns tracks played after this time"
                },
                "before": {
                    "type": "integer",
                    "description": "Unix timestamp in milliseconds - returns tracks played before this time"
                }
            }
        }
    }
]
