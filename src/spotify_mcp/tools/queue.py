"""Queue management tools for Spotify."""

from typing import Dict, Any, Optional
from spotify_mcp.spotify_client import SpotifyClient


def get_queue(client: SpotifyClient) -> Dict[str, Any]:
    """
    Get the user's current playback queue.
    
    Returns:
        Current queue including currently playing track and upcoming tracks
    """
    queue = client.queue()
    
    currently_playing = queue.get("currently_playing")
    queue_items = queue.get("queue", [])
    
    result = {
        "currently_playing": None,
        "queue": []
    }
    
    if currently_playing:
        result["currently_playing"] = {
            "name": currently_playing.get("name"),
            "uri": currently_playing.get("uri"),
            "id": currently_playing.get("id"),
            "artists": [
                {"name": a["name"], "uri": a["uri"]} 
                for a in currently_playing.get("artists", [])
            ],
            "album": {
                "name": currently_playing.get("album", {}).get("name"),
                "uri": currently_playing.get("album", {}).get("uri"),
            },
            "duration_ms": currently_playing.get("duration_ms"),
            "explicit": currently_playing.get("explicit", False)
        }
    
    result["queue"] = [
        {
            "name": track.get("name"),
            "uri": track.get("uri"),
            "id": track.get("id"),
            "artists": [
                {"name": a["name"], "uri": a["uri"]} 
                for a in track.get("artists", [])
            ],
            "album": {
                "name": track.get("album", {}).get("name"),
                "uri": track.get("album", {}).get("uri"),
            },
            "duration_ms": track.get("duration_ms"),
            "explicit": track.get("explicit", False)
        }
        for track in queue_items
    ]
    
    result["queue_length"] = len(queue_items)
    
    return result


def add_to_queue(client: SpotifyClient, uri: str, 
                 device_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Add a track to the user's playback queue.
    
    Args:
        uri: Spotify track URI (e.g., spotify:track:xxx)
        device_id: Device ID to add to queue (optional)
    
    Returns:
        Success message
    """
    # Ensure URI is in correct format
    if not uri.startswith("spotify:track:"):
        # Assume it's an ID and convert to URI
        uri = f"spotify:track:{uri}"
    
    client.add_to_queue(uri=uri, device_id=device_id)
    
    return {
        "success": True,
        "message": "Track added to queue",
        "track_uri": uri,
        "device_id": device_id or "default device"
    }


# Tool definitions for MCP
QUEUE_TOOLS = [
    {
        "name": "get_queue",
        "description": "Get the user's current playback queue, including the currently playing track and upcoming tracks.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "add_to_queue",
        "description": "Add a track to the user's playback queue.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "uri": {
                    "type": "string",
                    "description": "Spotify track URI or ID (e.g., 'spotify:track:xxx' or just the track ID)"
                },
                "device_id": {
                    "type": "string",
                    "description": "Device ID to add to queue (optional)"
                }
            },
            "required": ["uri"]
        }
    }
]
