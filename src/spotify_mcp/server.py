"""Spotify MCP Server - Control Spotify through AI.

A production-ready Model Context Protocol server that enables AI assistants
to seamlessly control Spotify. Natural language commands become API calls,
giving users intuitive voice control over their entire music experience.

69 tools organized by capability:
- Playback: Control your music (play, pause, skip, volume, devices)
- Discovery: Find and explore music (search)
- Library: Manage your saved content (tracks, albums)
- Artists: Explore artist catalogs
- Playlists: Create and modify playlists
- Queue: Manage what plays next
- User: Access profile and listening stats
- Categories: Browse Spotify content categories
- Episodes: Manage podcast episodes
- Shows: Browse and manage podcasts
- Tracks: Get track details
- Markets: Check Spotify availability by country

Note: Some API endpoints were deprecated by Spotify on November 27, 2024:
- Audio Features/Analysis, Recommendations, Related Artists
- Featured Playlists, Category Playlists, Genre Seeds
- Audiobook and Chapter endpoints (require Extended Quota Mode)
"""

import sys
import json
import asyncio
import os
from pathlib import Path
from typing import Any, Dict
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server
from dotenv import load_dotenv, find_dotenv

# Load environment variables first, before any imports that might need them
# Strategy: Try multiple approaches to find .env file

# Approach 1: Use find_dotenv to search up the directory tree
dotenv_path = find_dotenv(usecwd=True)

# Approach 2: If not found, calculate path relative to this file
if not dotenv_path:
    project_root = Path(__file__).parent.parent.parent
    potential_env = project_root / ".env"
    if potential_env.exists():
        dotenv_path = str(potential_env)

# Approach 3: Check if tokens are already in environment (from Claude Desktop config)
# If so, we don't need to load .env
has_tokens = os.getenv("SPOTIFY_ACCESS_TOKEN") and os.getenv("SPOTIFY_REFRESH_TOKEN")

# Load .env if we found it and don't already have tokens
if dotenv_path and not has_tokens:
    load_dotenv(dotenv_path)
elif not dotenv_path and not has_tokens:
    # Last resort: try loading from current directory
    load_dotenv()

from spotify_mcp.auth import get_spotify_client
from spotify_mcp.spotify_client import SpotifyClient

# Import all tools
from spotify_mcp.tools.playback import (
    play, pause, skip_next, skip_previous, get_current_playback,
    get_available_devices, transfer_playback, set_volume, set_shuffle,
    set_repeat, seek_to_position, get_recently_played, PLAYBACK_TOOLS
)
from spotify_mcp.tools.search import (
    SEARCH_TOOLS, search
)
from spotify_mcp.tools.library import (
    LIBRARY_TOOLS, get_saved_tracks, save_tracks,
    remove_saved_tracks, check_saved_tracks
)
from spotify_mcp.tools.albums import (
    ALBUM_TOOLS, get_album, get_several_albums, get_album_tracks,
    get_saved_albums, save_albums, remove_saved_albums, 
    check_saved_albums, get_new_releases
)
from spotify_mcp.tools.playlists import (
    PLAYLIST_TOOLS, get_user_playlists, get_playlist,
    create_playlist, add_tracks_to_playlist, remove_tracks_from_playlist,
    change_playlist_details, update_playlist_items,
    get_playlist_cover_image, add_custom_playlist_cover_image,
    get_user_playlists_by_id, follow_playlist, unfollow_playlist
)
from spotify_mcp.tools.queue import (
    QUEUE_TOOLS, get_queue, add_to_queue
)
from spotify_mcp.tools.user import (
    USER_TOOLS, get_current_user, get_top_items, get_user_profile,
    get_followed_artists, follow_artists_or_users, unfollow_artists_or_users,
    check_following_artists_or_users, check_current_user_follows_playlist
)
from spotify_mcp.tools.artists import (
    ARTIST_TOOLS, get_artist, get_several_artists, get_artist_albums,
    get_artist_top_tracks
)
from spotify_mcp.tools.audiobooks import AUDIOBOOK_TOOLS
from spotify_mcp.tools.categories import (
    CATEGORY_TOOLS, get_several_browse_categories, get_single_browse_category
)
from spotify_mcp.tools.chapters import CHAPTER_TOOLS
from spotify_mcp.tools.episodes import (
    EPISODE_TOOLS, get_episode, get_several_episodes, get_saved_episodes,
    save_episodes, remove_saved_episodes, check_saved_episodes
)
from spotify_mcp.tools.genres import GENRE_TOOLS
from spotify_mcp.tools.markets import (
    MARKET_TOOLS, get_available_markets
)
from spotify_mcp.tools.shows import (
    SHOW_TOOLS, get_show, get_several_shows, get_show_episodes,
    get_saved_shows, save_shows, remove_saved_shows, check_saved_shows
)
from spotify_mcp.tools.tracks import (
    TRACK_TOOLS, get_track, get_several_tracks
)


# Create server instance with metadata
app = Server("spotify")

# Global Spotify client (initialized on first use)
_spotify_client: SpotifyClient = None


def get_client() -> SpotifyClient:
    """Get or create Spotify client."""
    global _spotify_client
    if _spotify_client is None:
        import os
        # Check if tokens exist before trying to authenticate
        # This prevents interactive auth flow during MCP server startup
        if not os.getenv("SPOTIFY_ACCESS_TOKEN") or not os.getenv("SPOTIFY_REFRESH_TOKEN"):
            print("ERROR: No Spotify tokens found.", file=sys.stderr)
            print("Please run authentication first:", file=sys.stderr)
            print("  python -m spotify_mcp.auth", file=sys.stderr)
            raise RuntimeError("Spotify authentication required. Run: python -m spotify_mcp.auth")
        
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
    "get_recently_played": get_recently_played,
    
    # Search
    "search": search,
    
    # Library - Tracks
    "get_saved_tracks": get_saved_tracks,
    "save_tracks": save_tracks,
    "remove_saved_tracks": remove_saved_tracks,
    "check_saved_tracks": check_saved_tracks,
    
    # Albums
    "get_album": get_album,
    "get_several_albums": get_several_albums,
    "get_album_tracks": get_album_tracks,
    "get_saved_albums": get_saved_albums,
    "save_albums": save_albums,
    "remove_saved_albums": remove_saved_albums,
    "check_saved_albums": check_saved_albums,
    "get_new_releases": get_new_releases,
    
    # Playlists
    "get_user_playlists": get_user_playlists,
    "get_playlist": get_playlist,
    "create_playlist": create_playlist,
    "add_tracks_to_playlist": add_tracks_to_playlist,
    "remove_tracks_from_playlist": remove_tracks_from_playlist,
    "change_playlist_details": change_playlist_details,
    "update_playlist_items": update_playlist_items,
    "get_playlist_cover_image": get_playlist_cover_image,
    "add_custom_playlist_cover_image": add_custom_playlist_cover_image,
    "get_user_playlists_by_id": get_user_playlists_by_id,
    "follow_playlist": follow_playlist,
    "unfollow_playlist": unfollow_playlist,
    
    # Queue
    "get_queue": get_queue,
    "add_to_queue": add_to_queue,
    
    # User
    "get_current_user": get_current_user,
    "get_top_items": get_top_items,
    "get_user_profile": get_user_profile,
    "get_followed_artists": get_followed_artists,
    "follow_artists_or_users": follow_artists_or_users,
    "unfollow_artists_or_users": unfollow_artists_or_users,
    "check_following_artists_or_users": check_following_artists_or_users,
    "check_current_user_follows_playlist": check_current_user_follows_playlist,
    
    # Artists
    "get_artist": get_artist,
    "get_several_artists": get_several_artists,
    "get_artist_albums": get_artist_albums,
    "get_artist_top_tracks": get_artist_top_tracks,
    
    # Categories
    "get_several_browse_categories": get_several_browse_categories,
    "get_single_browse_category": get_single_browse_category,
    
    # Episodes
    "get_episode": get_episode,
    "get_several_episodes": get_several_episodes,
    "get_saved_episodes": get_saved_episodes,
    "save_episodes": save_episodes,
    "remove_saved_episodes": remove_saved_episodes,
    "check_saved_episodes": check_saved_episodes,
    
    # Markets
    "get_available_markets": get_available_markets,
    
    # Shows
    "get_show": get_show,
    "get_several_shows": get_several_shows,
    "get_show_episodes": get_show_episodes,
    "get_saved_shows": get_saved_shows,
    "save_shows": save_shows,
    "remove_saved_shows": remove_saved_shows,
    "check_saved_shows": check_saved_shows,
    
    # Tracks
    "get_track": get_track,
    "get_several_tracks": get_several_tracks,
}


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    all_tools = (
        PLAYBACK_TOOLS +
        SEARCH_TOOLS +
        LIBRARY_TOOLS +
        ALBUM_TOOLS +
        PLAYLIST_TOOLS +
        QUEUE_TOOLS +
        USER_TOOLS +
        ARTIST_TOOLS +
        AUDIOBOOK_TOOLS +
        CATEGORY_TOOLS +
        CHAPTER_TOOLS +
        EPISODE_TOOLS +
        GENRE_TOOLS +
        MARKET_TOOLS +
        SHOW_TOOLS +
        TRACK_TOOLS
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
        try:
            print("\nShutting down Spotify MCP server...", file=sys.stderr)
        except (ValueError, OSError):
            # stdout/stderr may be closed when running as MCP server
            pass
        sys.exit(0)


if __name__ == "__main__":
    run()
