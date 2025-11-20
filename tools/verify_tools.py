"""Verify all Spotify MCP tools are properly registered."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spotify_mcp.server import TOOL_FUNCTIONS
from spotify_mcp.tools.playback import PLAYBACK_TOOLS
from spotify_mcp.tools.search import SEARCH_TOOLS
from spotify_mcp.tools.library import LIBRARY_TOOLS
from spotify_mcp.tools.albums import ALBUM_TOOLS
from spotify_mcp.tools.artists import ARTIST_TOOLS
from spotify_mcp.tools.audiobooks import AUDIOBOOK_TOOLS
from spotify_mcp.tools.categories import CATEGORY_TOOLS
from spotify_mcp.tools.chapters import CHAPTER_TOOLS
from spotify_mcp.tools.episodes import EPISODE_TOOLS
from spotify_mcp.tools.genres import GENRE_TOOLS
from spotify_mcp.tools.markets import MARKET_TOOLS
from spotify_mcp.tools.playlists import PLAYLIST_TOOLS
from spotify_mcp.tools.queue import QUEUE_TOOLS
from spotify_mcp.tools.shows import SHOW_TOOLS
from spotify_mcp.tools.tracks import TRACK_TOOLS
from spotify_mcp.tools.user import USER_TOOLS


def main():
    """Verify tool registration and counts."""
    
    print("🎵 Spotify MCP Server - Tool Verification\n")
    print("=" * 50)
    
    # Category breakdown
    categories = [
        ("Playback Control", PLAYBACK_TOOLS),
        ("Search & Discovery", SEARCH_TOOLS),
        ("Library Management", LIBRARY_TOOLS),
        ("Album Operations", ALBUM_TOOLS),
        ("Artist Operations", ARTIST_TOOLS),
        ("Audiobook Operations", AUDIOBOOK_TOOLS),
        ("Category Browsing", CATEGORY_TOOLS),
        ("Chapter Access", CHAPTER_TOOLS),
        ("Episode Management", EPISODE_TOOLS),
        ("Genre Discovery", GENRE_TOOLS),
        ("Market Information", MARKET_TOOLS),
        ("Playlist Operations", PLAYLIST_TOOLS),
        ("Queue Management", QUEUE_TOOLS),
        ("Show Management", SHOW_TOOLS),
        ("Track Operations", TRACK_TOOLS),
        ("User Info", USER_TOOLS),
    ]
    
    total = 0
    for name, tools in categories:
        count = len(tools)
        total += count
        print(f"  {name:.<40} {count:>2} tools")
    
    print("=" * 50)
    print(f"  {'Total':.<40} {total:>2} tools")
    print()
    
    # Verify against TOOL_FUNCTIONS
    registered = len(TOOL_FUNCTIONS)
    print(f"✅ Registered in TOOL_FUNCTIONS: {registered}")
    
    if registered == total:
        print(f"✅ All {total} tools successfully registered!")
        return 0
    else:
        print(f"❌ Mismatch! Expected {total} but got {registered}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
