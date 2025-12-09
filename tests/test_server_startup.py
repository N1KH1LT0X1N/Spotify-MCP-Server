"""Test MCP server startup and tool listing."""

import sys
import json
import pytest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_server_initialization():
    """Test that the server module can be imported."""
    print("=" * 60)
    print("TEST: Server Module Import")
    print("=" * 60)
    
    try:
        from spotify_mcp import server
        print("✅ Server module imported successfully")
        
        # Check main components exist
        if hasattr(server, 'main'):
            print("✅ main() function exists")
        else:
            print("❌ main() function missing")
            pytest.fail("Test assertion failed")
        
        if hasattr(server, 'TOOL_FUNCTIONS'):
            print(f"✅ TOOL_FUNCTIONS exists with {len(server.TOOL_FUNCTIONS)} functions")
        else:
            print("❌ TOOL_FUNCTIONS missing")
            pytest.fail("Test assertion failed")
        
        pass  # Test passes
    except Exception as e:
        print(f"❌ Server initialization failed: {e}")
        import traceback
        traceback.print_exc()
        pytest.fail("Test assertion failed")


def test_list_tools():
    """Test the tool definitions."""
    print("\n" + "=" * 60)
    print("TEST: Tool Definitions")
    print("=" * 60)
    
    try:
        from spotify_mcp.tools.albums import ALBUM_TOOLS
        from spotify_mcp.tools.artists import ARTIST_TOOLS
        from spotify_mcp.tools.audiobooks import AUDIOBOOK_TOOLS
        from spotify_mcp.tools.categories import CATEGORY_TOOLS
        from spotify_mcp.tools.chapters import CHAPTER_TOOLS
        from spotify_mcp.tools.episodes import EPISODE_TOOLS
        from spotify_mcp.tools.genres import GENRE_TOOLS
        from spotify_mcp.tools.library import LIBRARY_TOOLS
        from spotify_mcp.tools.markets import MARKET_TOOLS
        from spotify_mcp.tools.playback import PLAYBACK_TOOLS
        from spotify_mcp.tools.playlists import PLAYLIST_TOOLS
        from spotify_mcp.tools.queue import QUEUE_TOOLS
        from spotify_mcp.tools.search import SEARCH_TOOLS
        from spotify_mcp.tools.shows import SHOW_TOOLS
        from spotify_mcp.tools.tracks import TRACK_TOOLS
        from spotify_mcp.tools.user import USER_TOOLS
        
        all_tools = (
            ALBUM_TOOLS + ARTIST_TOOLS + AUDIOBOOK_TOOLS + 
            CATEGORY_TOOLS + CHAPTER_TOOLS + EPISODE_TOOLS +
            GENRE_TOOLS + LIBRARY_TOOLS + MARKET_TOOLS +
            PLAYBACK_TOOLS + PLAYLIST_TOOLS + QUEUE_TOOLS +
            SEARCH_TOOLS + SHOW_TOOLS + TRACK_TOOLS + USER_TOOLS
        )
        
        print(f"📊 Total tools available: {len(all_tools)}")
        
        # Count by category
        categories = {
            "Playback": len(PLAYBACK_TOOLS),
            "Search": len(SEARCH_TOOLS),
            "Library": len(LIBRARY_TOOLS),
            "Albums": len(ALBUM_TOOLS),
            "Artists": len(ARTIST_TOOLS),
            "Audiobooks": len(AUDIOBOOK_TOOLS),
            "Categories": len(CATEGORY_TOOLS),
            "Chapters": len(CHAPTER_TOOLS),
            "Episodes": len(EPISODE_TOOLS),
            "Genres": len(GENRE_TOOLS),
            "Markets": len(MARKET_TOOLS),
            "Playlists": len(PLAYLIST_TOOLS),
            "Queue": len(QUEUE_TOOLS),
            "Shows": len(SHOW_TOOLS),
            "Tracks": len(TRACK_TOOLS),
            "Users": len(USER_TOOLS),
        }
        
        print("\n📋 Tools by Category:")
        for cat, count in categories.items():
            print(f"   {cat:.<20} {count:>2} tools")
        
        # Verify key tools exist
        tool_names = [t["name"] for t in all_tools]
        key_tools = [
            "play", "pause", "get_current_playback", "get_recently_played",
            "search",
            "create_playlist", "add_tracks_to_playlist",
            "get_current_user", "get_top_items"
        ]
        
        print("\n🔑 Key Tools Check:")
        all_present = True
        for key_tool in key_tools:
            present = key_tool in tool_names
            status = "✅" if present else "❌"
            print(f"   {status} {key_tool}")
            if not present:
                all_present = False
        
        # Accept 69+ tools (legacy tools modules have 69 tools)
        if len(all_tools) >= 69 and all_present:
            print(f"\n✅ All {len(all_tools)} tools available and key tools present!")
            pass  # Test passes
        elif len(all_tools) >= 69:
            print(f"\n⚠️  {len(all_tools)} tools found but some key tools missing")
            pytest.fail("Test assertion failed")
        else:
            print(f"\n❌ Expected 69+ tools, got {len(all_tools)}")
            pytest.fail("Test assertion failed")
            
    except Exception as e:
        print(f"❌ List tools test failed: {e}")
        import traceback
        traceback.print_exc()
        pytest.fail("Test assertion failed")


def test_tool_details():
    """Test that tool details are complete."""
    print("\n" + "=" * 60)
    print("TEST: Tool Details")
    print("=" * 60)
    
    try:
        from spotify_mcp.tools.playback import PLAYBACK_TOOLS
        from spotify_mcp.tools.search import SEARCH_TOOLS
        from spotify_mcp.tools.playlists import PLAYLIST_TOOLS
        
        # Check a few sample tools for completeness
        sample_tools_sets = [
            ("play", PLAYBACK_TOOLS),
            ("get_recently_played", PLAYBACK_TOOLS),
            ("search", SEARCH_TOOLS),
            ("create_playlist", PLAYLIST_TOOLS)
        ]
        
        all_valid = True
        for tool_name, tool_set in sample_tools_sets:
            tool = next((t for t in tool_set if t["name"] == tool_name), None)
            if not tool:
                print(f"❌ Tool '{tool_name}' not found")
                all_valid = False
                continue
            
            print(f"\n🔍 {tool_name}:")
            
            # Check required fields
            if "description" in tool and tool["description"]:
                print(f"   ✅ Description: {tool['description'][:60]}...")
            else:
                print(f"   ❌ Missing or empty description")
                all_valid = False
            
            if "inputSchema" in tool:
                schema = tool["inputSchema"]
                props = schema.get("properties", {})
                print(f"   ✅ Input schema with {len(props)} parameters")
            else:
                print(f"   ❌ Missing inputSchema")
                all_valid = False
        
        if all_valid:
            print("\n✅ Tool details are complete!")
            pass  # Test passes
        else:
            print("\n❌ Some tools have incomplete details")
            pytest.fail("Test assertion failed")
        
    except Exception as e:
        print(f"❌ Tool details test failed: {e}")
        import traceback
        traceback.print_exc()
        pytest.fail("Test assertion failed")


def main():
    """Run startup tests."""
    print("\n" + "🎵" * 30)
    print("   MCP SERVER STARTUP TEST")
    print("🎵" * 30 + "\n")
    
    results = {
        "Server Module Import": test_server_initialization(),
        "Tool Definitions": test_list_tools(),
        "Tool Details": test_tool_details(),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 SERVER STARTUP TESTS PASSED!")
    else:
        print("⚠️  Some tests failed.")
    
    print("=" * 60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
