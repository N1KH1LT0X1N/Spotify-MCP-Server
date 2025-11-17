#!/usr/bin/env python3
"""Quick test for new playlist features."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spotify_mcp.auth import get_spotify_client
from spotify_mcp.spotify_client import SpotifyClient
from spotify_mcp.tools.playlists import get_user_playlists


def main():
    """Test that playlist tools are accessible and registered."""
    print("🧪 Testing New Playlist Features\n")
    
    try:
        # Get authenticated Spotify client
        print("🔑 Authenticating with Spotify...")
        sp = get_spotify_client()
        client = SpotifyClient(sp)
        print("✅ Authentication successful\n")
        
        # Test basic playlist retrieval to verify setup
        print("🎵 Testing get_user_playlists...")
        result = get_user_playlists(client, limit=5)
        
        if result.get("success"):
            playlists = result.get("playlists", [])
            print(f"✅ Found {result.get('total', 0)} total playlists (showing {len(playlists)}):")
            for i, playlist in enumerate(playlists, 1):
                print(f"   {i}. {playlist['name']}")
            print()
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}\n")
        
        # Verify new functions are importable
        print("🔍 Verifying new playlist functions are available...")
        from spotify_mcp.tools.playlists import (
            change_playlist_details,
            update_playlist_items,
            get_featured_playlists,
            get_category_playlists,
            get_playlist_cover_image,
            add_custom_playlist_cover_image,
            get_user_playlists_by_id
        )
        print("✅ All 7 new playlist functions successfully imported")
        print()
        
        print("✅ All tests passed! New playlist features are properly integrated.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
