"""Spotify MCP Server - Control Spotify through AI.

A production-ready Model Context Protocol server that enables AI assistants
to seamlessly control Spotify. Natural language commands become API calls,
giving users intuitive voice control over their entire music experience.

86 tools organized by capability:
- Playback: Control your music (play, pause, skip, volume, devices)
- Discovery: Find and explore music (search, recommendations)
- Library: Manage your saved content (tracks, albums, audiobooks)
- Artists: Explore artist catalogs and relationships
- Playlists: Create and modify playlists
- Queue: Manage what plays next
- User: Access profile and listening stats
- Categories: Browse Spotify content categories
- Chapters: Access audiobook chapters
- Episodes: Manage podcast episodes
- Shows: Browse and manage podcasts
- Tracks: Get track details and audio analysis
- Genres: Discover music by genre
- Markets: Check Spotify availability by country

8 resources for efficient data access:
- Current playback state
- User playlists
- Recently played tracks
- User profile
- Available devices
- Saved tracks/albums
- Playback queue

8 prompts for common interactions:
- Discover new music
- Create playlists
- Analyze listening habits
- Control playback
- Explore artists
- Find similar music
"""

import sys
import json
import asyncio
import os
from pathlib import Path
from typing import Any, Dict
from mcp.server import Server
from mcp.types import Tool, TextContent, Resource, Prompt, PromptMessage
from mcp.server.stdio import stdio_server

from spotify_mcp.auth import get_spotify_client
from spotify_mcp.spotify_client import SpotifyClient
from spotify_mcp.resources import get_resources
from spotify_mcp.prompts import SpotifyPrompts

# Logging infrastructure
from spotify_mcp.infrastructure.logging import (
    get_logger,
    setup_logging,
    LogLevel,
    log_context,
    set_correlation_id
)

# Initialize logger for this module
logger = get_logger(__name__)

# Optional metrics integration
try:
    from spotify_mcp.infrastructure.metrics import get_metrics_collector
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    get_metrics_collector = None

# Resilience infrastructure
try:
    from spotify_mcp.infrastructure.resilience import (
        get_circuit_breaker_registry,
        get_rate_limiter,
        get_health_system,
        CircuitBreakerOpenError
    )
    RESILIENCE_AVAILABLE = True
except ImportError:
    RESILIENCE_AVAILABLE = False
    logger.warning("Resilience infrastructure not available")

# Cache infrastructure
try:
    from spotify_mcp.infrastructure.cache import (
        get_cache_invalidator,
        get_cache_warmer,
        warm_cache_on_startup
    )
    CACHE_ENHANCEMENTS_AVAILABLE = True
except ImportError:
    CACHE_ENHANCEMENTS_AVAILABLE = False
    logger.warning("Cache enhancements not available")

# Import all tools
from spotify_mcp.tools.playback import (
    play, pause, skip_next, skip_previous, get_current_playback,
    get_available_devices, transfer_playback, set_volume, set_shuffle,
    set_repeat, seek_to_position, get_recently_played, PLAYBACK_TOOLS
)
from spotify_mcp.tools.search import (
    SEARCH_TOOLS, search, get_recommendations
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
    change_playlist_details, update_playlist_items, get_featured_playlists,
    get_category_playlists, get_playlist_cover_image, add_custom_playlist_cover_image,
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
    get_artist_top_tracks, get_artist_related_artists
)
from spotify_mcp.tools.audiobooks import (
    AUDIOBOOK_TOOLS, get_audiobook, get_several_audiobooks, get_audiobook_chapters,
    get_saved_audiobooks, save_audiobooks, remove_saved_audiobooks, check_saved_audiobooks
)
from spotify_mcp.tools.categories import (
    CATEGORY_TOOLS, get_several_browse_categories, get_single_browse_category
)
from spotify_mcp.tools.chapters import (
    CHAPTER_TOOLS, get_chapter, get_several_chapters
)
from spotify_mcp.tools.episodes import (
    EPISODE_TOOLS, get_episode, get_several_episodes, get_saved_episodes,
    save_episodes, remove_saved_episodes, check_saved_episodes
)
from spotify_mcp.tools.genres import (
    GENRE_TOOLS, get_available_genre_seeds
)
from spotify_mcp.tools.markets import (
    MARKET_TOOLS, get_available_markets
)
from spotify_mcp.tools.shows import (
    SHOW_TOOLS, get_show, get_several_shows, get_show_episodes,
    get_saved_shows, save_shows, remove_saved_shows, check_saved_shows
)
from spotify_mcp.tools.tracks import (
    TRACK_TOOLS, get_track, get_several_tracks, get_tracks_audio_features,
    get_track_audio_features, get_track_audio_analysis
)


# Create server instance with metadata
app = Server("spotify")

# Global Spotify client (initialized on first use)
_spotify_client: SpotifyClient = None
_initialized: bool = False


async def initialize_infrastructure():
    """Initialize all infrastructure components on startup."""
    global _initialized

    if _initialized:
        return

    logger.info("Initializing infrastructure components...")

    # Initialize resilience components
    if RESILIENCE_AVAILABLE:
        try:
            # Setup circuit breaker for Spotify API
            registry = get_circuit_breaker_registry()
            registry.get_or_create(
                name="spotify_api",
                failure_threshold=5,
                recovery_timeout=60,
                success_threshold=2,
                timeout=30.0
            )
            logger.info("Circuit breaker initialized")

            # Rate limiter is already initialized as singleton
            logger.info("Rate limiter initialized")

            # Setup health checks
            health_system = get_health_system()
            # Health checks will be registered when components are available
            logger.info("Health check system initialized")

        except Exception as e:
            logger.error(f"Failed to initialize resilience infrastructure: {e}")

    # Warm cache on startup
    if CACHE_ENHANCEMENTS_AVAILABLE:
        try:
            client = get_client()
            # Cache warming will happen asynchronously
            asyncio.create_task(warm_cache_on_startup(client.sp, None))
            logger.info("Cache warming initiated")
        except Exception as e:
            logger.error(f"Failed to warm cache: {e}")

    _initialized = True
    logger.info("Infrastructure initialization complete")


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
    "get_recently_played": get_recently_played,
    
    # Search
    "search": search,
    "get_recommendations": get_recommendations,
    
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
    "get_featured_playlists": get_featured_playlists,
    "get_category_playlists": get_category_playlists,
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
    "get_artist_related_artists": get_artist_related_artists,
    
    # Audiobooks
    "get_audiobook": get_audiobook,
    "get_several_audiobooks": get_several_audiobooks,
    "get_audiobook_chapters": get_audiobook_chapters,
    "get_saved_audiobooks": get_saved_audiobooks,
    "save_audiobooks": save_audiobooks,
    "remove_saved_audiobooks": remove_saved_audiobooks,
    "check_saved_audiobooks": check_saved_audiobooks,
    
    # Categories
    "get_several_browse_categories": get_several_browse_categories,
    "get_single_browse_category": get_single_browse_category,
    
    # Chapters
    "get_chapter": get_chapter,
    "get_several_chapters": get_several_chapters,
    
    # Episodes
    "get_episode": get_episode,
    "get_several_episodes": get_several_episodes,
    "get_saved_episodes": get_saved_episodes,
    "save_episodes": save_episodes,
    "remove_saved_episodes": remove_saved_episodes,
    "check_saved_episodes": check_saved_episodes,
    
    # Genres
    "get_available_genre_seeds": get_available_genre_seeds,
    
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
    "get_tracks_audio_features": get_tracks_audio_features,
    "get_track_audio_features": get_track_audio_features,
    "get_track_audio_analysis": get_track_audio_analysis,
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


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List all available resources."""
    client = get_client()
    resources_handler = get_resources(client)
    resource_defs = resources_handler.list_all()

    return [
        Resource(
            uri=res["uri"],
            name=res["name"],
            description=res["description"],
            mimeType=res.get("mimeType", "application/json")
        )
        for res in resource_defs
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource by URI."""
    client = get_client()
    resources_handler = get_resources(client)

    try:
        data = await resources_handler.read(uri)
        return json.dumps(data, indent=2)
    except Exception as e:
        logger.error(f"Failed to read resource {uri}: {e}", exc_info=True)
        return json.dumps({
            "error": str(e),
            "uri": uri
        }, indent=2)


@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List all available prompts."""
    prompt_defs = SpotifyPrompts.list_all()

    return [
        Prompt(
            name=p["name"],
            description=p["description"],
            arguments=[
                {
                    "name": arg["name"],
                    "description": arg["description"],
                    "required": arg.get("required", False)
                }
                for arg in p.get("arguments", [])
            ] if p.get("arguments") else None
        )
        for p in prompt_defs
    ]


@app.get_prompt()
async def get_prompt(name: str, arguments: Dict[str, str] = None) -> Dict[str, Any]:
    """Get a prompt by name with optional arguments."""
    try:
        prompt_data = SpotifyPrompts.get(name, arguments)
        return prompt_data
    except Exception as e:
        logger.error(f"Failed to get prompt {name}: {e}", exc_info=True)
        return {
            "description": f"Error loading prompt: {name}",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                }
            ]
        }


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute a tool with given arguments."""
    import time
    import uuid

    # Ensure infrastructure is initialized
    await initialize_infrastructure()

    # Generate correlation ID for this request
    correlation_id = str(uuid.uuid4())
    set_correlation_id(correlation_id)

    # Track metrics if available
    start_time = time.time()
    status = 'success'

    # Increment active requests
    if METRICS_AVAILABLE:
        collector = get_metrics_collector()
        collector.increment_active_requests()

    # Use log context for this tool execution
    with log_context(tool=name, correlation_id=correlation_id):
        logger.debug("Tool call started", extra={"arguments": arguments})

        try:
            # Rate limiting
            if RESILIENCE_AVAILABLE:
                rate_limiter = get_rate_limiter()
                wait_time = await rate_limiter.acquire()
                if wait_time > 0:
                    logger.info(f"Rate limited, waited {wait_time:.2f}s")

            # Get the function for this tool
            if name not in TOOL_FUNCTIONS:
                logger.error("Unknown tool requested", extra={"tool": name})
                raise ValueError(f"Unknown tool: {name}")

            tool_func = TOOL_FUNCTIONS[name]
            client = get_client()

            # Execute through circuit breaker if available
            if RESILIENCE_AVAILABLE:
                circuit_breaker = get_circuit_breaker_registry().get_or_create("spotify_api")
                try:
                    # Call the function with arguments through circuit breaker
                    async def execute_tool():
                        if arguments:
                            return tool_func(client, **arguments)
                        else:
                            return tool_func(client)

                    result = await circuit_breaker.call(execute_tool)
                except CircuitBreakerOpenError as e:
                    logger.warning("Circuit breaker is open", extra={"circuit": "spotify_api"})
                    raise Exception("Spotify API is temporarily unavailable (circuit breaker open)")
            else:
                # Call without circuit breaker
                if arguments:
                    result = tool_func(client, **arguments)
                else:
                    result = tool_func(client)

            # Cache invalidation for mutation operations
            if CACHE_ENHANCEMENTS_AVAILABLE:
                await handle_cache_invalidation(name, arguments, result)

            logger.info("Tool call completed successfully")

            # Format result as JSON
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        except Exception as e:
            status = 'error'
            logger.error("Tool call failed", exc_info=True, extra={"error": str(e)})

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

        finally:
            # Record metrics
            if METRICS_AVAILABLE:
                duration = time.time() - start_time
                collector.record_tool_call(name, duration, status)
                collector.decrement_active_requests()
                logger.debug("Tool metrics recorded", extra={"duration_ms": duration * 1000, "status": status})


async def handle_cache_invalidation(tool_name: str, arguments: Dict[str, Any], result: Any):
    """Handle cache invalidation after mutation operations."""
    if not CACHE_ENHANCEMENTS_AVAILABLE:
        return

    invalidator = get_cache_invalidator()

    # Map tool names to cache invalidation operations
    mutation_handlers = {
        # Playlist mutations
        "add_tracks_to_playlist": lambda: invalidator.invalidate_playlist(arguments.get("playlist_id")),
        "remove_tracks_from_playlist": lambda: invalidator.invalidate_playlist(arguments.get("playlist_id")),
        "create_playlist": lambda: invalidator.invalidate_on_mutation("playlist", None, "create"),
        "change_playlist_details": lambda: invalidator.invalidate_playlist(arguments.get("playlist_id")),
        "update_playlist_items": lambda: invalidator.invalidate_playlist(arguments.get("playlist_id")),
        "follow_playlist": lambda: invalidator.invalidate_on_mutation("playlist", arguments.get("playlist_id"), "follow"),
        "unfollow_playlist": lambda: invalidator.invalidate_on_mutation("playlist", arguments.get("playlist_id"), "unfollow"),

        # Library mutations
        "save_tracks": lambda: invalidator.invalidate_library(),
        "remove_saved_tracks": lambda: invalidator.invalidate_library(),
        "save_albums": lambda: invalidator.invalidate_on_mutation("album", None, "save"),
        "remove_saved_albums": lambda: invalidator.invalidate_on_mutation("album", None, "remove"),
        "save_shows": lambda: invalidator.invalidate_on_mutation("show", None, "save"),
        "remove_saved_shows": lambda: invalidator.invalidate_on_mutation("show", None, "remove"),
        "save_episodes": lambda: invalidator.invalidate_on_mutation("episode", None, "save"),
        "remove_saved_episodes": lambda: invalidator.invalidate_on_mutation("episode", None, "remove"),
        "save_audiobooks": lambda: invalidator.invalidate_on_mutation("audiobook", None, "save"),
        "remove_saved_audiobooks": lambda: invalidator.invalidate_on_mutation("audiobook", None, "remove"),

        # Playback mutations
        "play": lambda: invalidator.invalidate_playback(),
        "pause": lambda: invalidator.invalidate_playback(),
        "skip_next": lambda: invalidator.invalidate_playback(),
        "skip_previous": lambda: invalidator.invalidate_playback(),
        "transfer_playback": lambda: invalidator.invalidate_devices(),
        "set_volume": lambda: invalidator.invalidate_playback(),
        "set_shuffle": lambda: invalidator.invalidate_playback(),
        "set_repeat": lambda: invalidator.invalidate_playback(),
        "seek_to_position": lambda: invalidator.invalidate_playback(),

        # Queue mutations
        "add_to_queue": lambda: invalidator.invalidate_queue(),

        # Follow mutations
        "follow_artists_or_users": lambda: invalidator.invalidate_on_mutation("artist", None, "follow"),
        "unfollow_artists_or_users": lambda: invalidator.invalidate_on_mutation("artist", None, "unfollow"),
    }

    # Execute invalidation if this is a mutation operation
    if tool_name in mutation_handlers:
        try:
            await mutation_handlers[tool_name]()
            logger.debug(f"Cache invalidated for {tool_name}")
        except Exception as e:
            logger.error(f"Failed to invalidate cache for {tool_name}: {e}")


async def main():
    """Main entry point for the server."""
    # Initialize infrastructure on server start
    await initialize_infrastructure()

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def run():
    """Run the server (sync wrapper)."""
    # Setup logging based on environment
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_format = os.getenv("LOG_FORMAT", "human")  # "human" or "json"

    try:
        setup_logging(
            level=LogLevel[log_level],
            format_type=log_format
        )
    except KeyError:
        # Fallback to INFO if invalid log level
        setup_logging(level=LogLevel.INFO, format_type=log_format)

    logger.info("Starting Spotify MCP Server", extra={
        "version": "1.1.0",
        "log_level": log_level,
        "log_format": log_format
    })

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received shutdown signal, stopping server...")
        sys.exit(0)
    except Exception as e:
        logger.critical("Server crashed", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run()
