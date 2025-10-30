"""Main MCP server implementation for Spotify."""

import sys
import json
import asyncio
from typing import Any, Dict
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from spotify_mcp.auth import get_spotify_client
from spotify_mcp.spotify_client import SpotifyClient

# Import all tools
from spotify_mcp.tools.playback import (
    PLAYBACK_TOOLS, play, pause, skip_next, skip_previous,
    get_current_playback, get_available_devices, transfer_playback,
    set_volume, set_shuffle, set_repeat, seek_to_position
)
from spotify_mcp.tools.search import (
    SEARCH_TOOLS, search, get_recommendations
)
from spotify_mcp.tools.library import (
    LIBRARY_TOOLS, get_saved_tracks, save_tracks,
    remove_saved_tracks, check_saved_tracks
)
from spotify_mcp.tools.playlists import (
    PLAYLIST_TOOLS, get_user_playlists, get_playlist,
    create_playlist, add_tracks_to_playlist, remove_tracks_from_playlist
)
from spotify_mcp.tools.queue import (
    QUEUE_TOOLS, get_queue, add_to_queue
)
from spotify_mcp.tools.user import (
    USER_TOOLS, get_current_user, get_top_items
)


# Create server instance
app = Server("spotify-mcp")

# Global Spotify client (initialized on first use)
_spotify_client: SpotifyClient = None


def get_client() -> SpotifyClient:
    """Get or create Spotify client."""
    global _spotify_client
    if _spotify_client is None:
        sp = get_spotify_client()
        _spotify_client = SpotifyClient(sp)
    return _spotify_client


# Tool name to function mapping
TOOL_FUNCTIONS = {
    # Playback
    "play": play,
    "pause": pause,
    "skip_next": skip_next,
    "skip_previous": skip_previous,
    "get_current_playback": get_current_playback,
    "get_available_devices": get_available_devices,
    "transfer_playback": transfer_playback,
    "set_volume": set_volume,
    "set_shuffle": set_shuffle,
    "set_repeat": set_repeat,
    "seek_to_position": seek_to_position,
    
    # Search
    "search": search,
    "get_recommendations": get_recommendations,
    
    # Library
    "get_saved_tracks": get_saved_tracks,
    "save_tracks": save_tracks,
    "remove_saved_tracks": remove_saved_tracks,
    "check_saved_tracks": check_saved_tracks,
    
    # Playlists
    "get_user_playlists": get_user_playlists,
    "get_playlist": get_playlist,
    "create_playlist": create_playlist,
    "add_tracks_to_playlist": add_tracks_to_playlist,
    "remove_tracks_from_playlist": remove_tracks_from_playlist,
    
    # Queue
    "get_queue": get_queue,
    "add_to_queue": add_to_queue,
    
    # User
    "get_current_user": get_current_user,
    "get_top_items": get_top_items,
}


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    all_tools = (
        PLAYBACK_TOOLS +
        SEARCH_TOOLS +
        LIBRARY_TOOLS +
        PLAYLIST_TOOLS +
        QUEUE_TOOLS +
        USER_TOOLS
    )
    
    return [
        Tool(
            name=tool["name"],
            description=tool["description"],
            inputSchema=tool["inputSchema"]
        )
        for tool in all_tools
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute a tool with given arguments."""
    try:
        # Get the function for this tool
        if name not in TOOL_FUNCTIONS:
            raise ValueError(f"Unknown tool: {name}")
        
        tool_func = TOOL_FUNCTIONS[name]
        client = get_client()
        
        # Call the function with arguments
        if arguments:
            result = tool_func(client, **arguments)
        else:
            result = tool_func(client)
        
        # Format result as JSON
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    except Exception as e:
        # Return error as text
        error_response = {
            "error": str(e),
            "tool": name,
            "arguments": arguments
        }
        return [TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


async def main():
    """Main entry point for the server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def run():
    """Run the server (sync wrapper)."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down Spotify MCP server...")
        sys.exit(0)


if __name__ == "__main__":
    run()
