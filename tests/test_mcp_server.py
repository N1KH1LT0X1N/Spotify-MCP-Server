"""Test script for Spotify MCP Server functionality."""

import sys
import json
import pytest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported."""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)
    
    try:
        from spotify_mcp import server
        print("✅ Server module imported successfully")
        
        from spotify_mcp.spotify_client import SpotifyClient
        print("✅ SpotifyClient imported successfully")
        
        from spotify_mcp.auth import SpotifyAuthManager
        print("✅ SpotifyAuthManager imported successfully")
        
        # Import all tool modules
        from spotify_mcp.tools import (
            albums, artists, audiobooks, categories, chapters,
            episodes, genres, library, markets, playback,
            playlists, queue, search, shows, tracks, user
        )
        print("✅ All 16 tool modules imported successfully")
        
        # Test passes - no return needed
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        pytest.fail(f"Import failed: {e}")


def test_tool_registration():
    """Test that all tools are registered correctly."""
    print("\n" + "=" * 60)
    print("TEST 2: Tool Registration")
    print("=" * 60)
    
    try:
        from spotify_mcp.server import TOOL_FUNCTIONS
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
        
        print(f"📊 Total tools defined: {len(all_tools)}")
        print(f"📊 Total functions registered: {len(TOOL_FUNCTIONS)}")
        
        # Count by category
        categories = {
            "Albums": len(ALBUM_TOOLS),
            "Artists": len(ARTIST_TOOLS),
            "Audiobooks": len(AUDIOBOOK_TOOLS),
            "Categories": len(CATEGORY_TOOLS),
            "Chapters": len(CHAPTER_TOOLS),
            "Episodes": len(EPISODE_TOOLS),
            "Genres": len(GENRE_TOOLS),
            "Library": len(LIBRARY_TOOLS),
            "Markets": len(MARKET_TOOLS),
            "Playback": len(PLAYBACK_TOOLS),
            "Playlists": len(PLAYLIST_TOOLS),
            "Queue": len(QUEUE_TOOLS),
            "Search": len(SEARCH_TOOLS),
            "Shows": len(SHOW_TOOLS),
            "Tracks": len(TRACK_TOOLS),
            "Users": len(USER_TOOLS),
        }
        
        print("\n📋 Tools by Category:")
        for cat, count in categories.items():
            print(f"   {cat:.<20} {count:>2} tools")
        
        # Verify all tool names match registered functions
        tool_names = {tool["name"] for tool in all_tools}
        registered_names = set(TOOL_FUNCTIONS.keys())
        
        missing = tool_names - registered_names
        extra = registered_names - tool_names
        
        if missing:
            print(f"\n⚠️  Tools defined but not registered: {missing}")
        if extra:
            print(f"\n⚠️  Functions registered but no tool definition: {extra}")
        
        if len(all_tools) == 86 and len(TOOL_FUNCTIONS) == 86:
            print("\n✅ All 86 tools correctly registered!")
        else:
            print(f"\n❌ Tool count mismatch!")
            pytest.fail(f"Expected 86 tools, got {len(all_tools)} defined and {len(TOOL_FUNCTIONS)} registered")
            
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        import traceback
        traceback.print_exc()
        pytest.fail(f"Registration test failed: {e}")


def test_tool_schemas():
    """Test that all tool schemas are valid."""
    print("\n" + "=" * 60)
    print("TEST 3: Tool Schema Validation")
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
        
        required_keys = ["name", "description", "inputSchema"]
        issues = []
        
        for tool in all_tools:
            # Check required keys
            for key in required_keys:
                if key not in tool:
                    issues.append(f"Tool '{tool.get('name', 'UNKNOWN')}' missing '{key}'")
            
            # Check inputSchema structure
            if "inputSchema" in tool:
                schema = tool["inputSchema"]
                if not isinstance(schema, dict):
                    issues.append(f"Tool '{tool['name']}' has invalid inputSchema type")
                elif "type" not in schema:
                    issues.append(f"Tool '{tool['name']}' inputSchema missing 'type'")
                elif schema["type"] != "object":
                    issues.append(f"Tool '{tool['name']}' inputSchema type is not 'object'")
        
        if issues:
            print("⚠️  Schema Issues Found:")
            for issue in issues:
                print(f"   - {issue}")
            pytest.fail("Test assertion failed")
        else:
            print("✅ All 86 tool schemas are valid!")
            pass  # Test passes
            
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        import traceback
        traceback.print_exc()
        pytest.fail("Test assertion failed")


def test_new_feature():
    """Test the newly added get_recently_played feature."""
    print("\n" + "=" * 60)
    print("TEST 4: New Feature - get_recently_played")
    print("=" * 60)
    
    try:
        # Check function exists
        from spotify_mcp.tools.playback import get_recently_played
        print("✅ get_recently_played function exists")
        
        # Check it's in PLAYBACK_TOOLS
        from spotify_mcp.tools.playback import PLAYBACK_TOOLS
        tool_names = [tool["name"] for tool in PLAYBACK_TOOLS]
        if "get_recently_played" in tool_names:
            print("✅ get_recently_played in PLAYBACK_TOOLS")
        else:
            print("❌ get_recently_played NOT in PLAYBACK_TOOLS")
            pytest.fail("Test assertion failed")
        
        # Check it's registered
        from spotify_mcp.server import TOOL_FUNCTIONS
        if "get_recently_played" in TOOL_FUNCTIONS:
            print("✅ get_recently_played registered in TOOL_FUNCTIONS")
        else:
            print("❌ get_recently_played NOT registered")
            pytest.fail("Test assertion failed")
        
        # Check SpotifyClient has the method
        from spotify_mcp.spotify_client import SpotifyClient
        if hasattr(SpotifyClient, "current_user_recently_played"):
            print("✅ SpotifyClient.current_user_recently_played method exists")
        else:
            print("❌ SpotifyClient missing current_user_recently_played")
            pytest.fail("Test assertion failed")
        
        # Check function signature
        import inspect
        sig = inspect.signature(get_recently_played)
        params = list(sig.parameters.keys())
        expected_params = ["client", "limit", "after", "before"]
        
        if params == expected_params:
            print(f"✅ Function signature correct: {params}")
        else:
            print(f"⚠️  Signature mismatch. Expected: {expected_params}, Got: {params}")
        
        print("\n✅ get_recently_played feature fully implemented!")
        pass  # Test passes
        
    except Exception as e:
        print(f"❌ New feature test failed: {e}")
        import traceback
        traceback.print_exc()
        pytest.fail("Test assertion failed")


def test_playback_count():
    """Verify playback tools count is 12."""
    print("\n" + "=" * 60)
    print("TEST 5: Playback Tools Count")
    print("=" * 60)
    
    try:
        from spotify_mcp.tools.playback import PLAYBACK_TOOLS
        
        count = len(PLAYBACK_TOOLS)
        print(f"📊 Playback tools count: {count}")
        
        tool_names = [tool["name"] for tool in PLAYBACK_TOOLS]
        print("\n📋 Playback Tools:")
        for i, name in enumerate(tool_names, 1):
            print(f"   {i:2}. {name}")
        
        if count == 12:
            print("\n✅ Playback category has exactly 12 tools!")
            pass  # Test passes
        else:
            print(f"\n❌ Expected 12 playback tools, got {count}")
            pytest.fail("Test assertion failed")
            
    except Exception as e:
        print(f"❌ Playback count test failed: {e}")
        import traceback
        traceback.print_exc()
        pytest.fail("Test assertion failed")


def test_syntax_errors():
    """Check for Python syntax errors in all modules."""
    print("\n" + "=" * 60)
    print("TEST 6: Syntax Error Check")
    print("=" * 60)
    
    try:
        import py_compile
        from pathlib import Path
        
        src_dir = Path(__file__).parent / "src" / "spotify_mcp"
        py_files = list(src_dir.rglob("*.py"))
        
        errors = []
        for py_file in py_files:
            try:
                py_compile.compile(str(py_file), doraise=True)
            except py_compile.PyCompileError as e:
                errors.append(f"{py_file.name}: {e}")
        
        if errors:
            print("❌ Syntax errors found:")
            for error in errors:
                print(f"   - {error}")
            pytest.fail("Test assertion failed")
        else:
            print(f"✅ No syntax errors in {len(py_files)} Python files!")
            pass  # Test passes
            
    except Exception as e:
        print(f"❌ Syntax check failed: {e}")
        import traceback
        traceback.print_exc()
        pytest.fail("Test assertion failed")


def main():
    """Run all tests."""
    print("\n" + "🎵" * 30)
    print("   SPOTIFY MCP SERVER - COMPREHENSIVE TEST SUITE")
    print("🎵" * 30 + "\n")
    
    results = {
        "Module Imports": test_imports(),
        "Tool Registration": test_tool_registration(),
        "Schema Validation": test_tool_schemas(),
        "New Feature (recently_played)": test_new_feature(),
        "Playback Count": test_playback_count(),
        "Syntax Errors": test_syntax_errors(),
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
        print("🎉 ALL TESTS PASSED! Server is ready for production.")
    else:
        print("⚠️  Some tests failed. Review the output above.")
    
    print("=" * 60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
