"""
Test mutation endpoints that were skipped in the main test.

This script tests write/mutation operations by:
1. Creating temporary test resources
2. Testing the operations
3. Cleaning up after

Note: This will create a test playlist and modify your library temporarily!
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@dataclass
class MutationTestResult:
    """Result of a mutation test."""
    tool_name: str
    category: str
    status: str  # WORKING, RESTRICTED, PREMIUM_REQUIRED, ERROR
    error_message: str = ""
    notes: str = ""


class MutationTester:
    """Tests mutation operations on Spotify API."""
    
    # Sample data for testing
    SAMPLE_TRACK_ID = "4iV5W9uYEdYUVa79Axb7Rh"  # Hotline Bling
    SAMPLE_TRACK_URI = "spotify:track:4iV5W9uYEdYUVa79Axb7Rh"
    SAMPLE_ALBUM_ID = "4aawyAB9vmqN3uQ7FjRGTy"  # Global Warming
    SAMPLE_ARTIST_ID = "3TVXtAsR1Inumwj472S9r4"  # Drake
    SAMPLE_SHOW_ID = "5CfCWKI5pZ28U0uOzXkDHe"  # TED Talks Daily
    SAMPLE_EPISODE_ID = "3Ll0kcZvNFdquWSrVfDJgI"  # A valid episode
    
    def __init__(self):
        self.results: List[MutationTestResult] = []
        self.client = None
        self.user_id = None
        self.test_playlist_id = None
        
    def setup(self):
        """Initialize Spotify client."""
        print("🔐 Authenticating with Spotify...")
        try:
            from spotify_mcp.auth import get_spotify_client
            from spotify_mcp.spotify_client import SpotifyClient
            
            sp = get_spotify_client()
            self.client = SpotifyClient(sp)
            
            user = self.client.current_user()
            self.user_id = user.get("id")
            print(f"✅ Authenticated as: {user.get('display_name', 'Unknown')} ({self.user_id})")
            return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    def test_mutation(self, tool_name: str, category: str, 
                      test_func, cleanup_func=None, notes: str = "") -> MutationTestResult:
        """Test a mutation operation."""
        result = MutationTestResult(
            tool_name=tool_name,
            category=category,
            status="UNKNOWN",
            notes=notes
        )
        
        try:
            test_func()
            result.status = "WORKING"
            print(f"  ✅ {tool_name}")
            
            # Cleanup if provided
            if cleanup_func:
                try:
                    cleanup_func()
                except Exception as e:
                    print(f"     ⚠️ Cleanup warning: {e}")
                    
        except Exception as e:
            error_str = str(e)
            
            if "403" in error_str or "Forbidden" in error_str.lower():
                if "PREMIUM_REQUIRED" in error_str:
                    result.status = "PREMIUM_REQUIRED"
                    print(f"  💎 {tool_name} - Premium required")
                else:
                    result.status = "RESTRICTED"
                    print(f"  🚫 {tool_name} - Restricted (403)")
            elif "404" in error_str:
                result.status = "ERROR"
                print(f"  ❌ {tool_name} - Not found (404)")
            elif "NO_ACTIVE_DEVICE" in error_str:
                result.status = "PREMIUM_REQUIRED"
                print(f"  💎 {tool_name} - Needs active device (Premium)")
            elif "has no attribute" in error_str:
                result.status = "NOT_IMPLEMENTED"
                print(f"  🔧 {tool_name} - Not in spotipy")
            else:
                result.status = "ERROR"
                print(f"  ❌ {tool_name} - Error: {error_str[:60]}...")
                
            result.error_message = error_str
        
        time.sleep(0.3)  # Rate limiting
        return result

    def run_all_tests(self):
        """Run all mutation tests."""
        from spotify_mcp.tools import playback, library, albums, playlists
        from spotify_mcp.tools import queue, user, audiobooks, episodes, shows
        
        print("\n" + "="*60)
        print("🧪 MUTATION ENDPOINT TESTING")
        print("="*60 + "\n")
        
        # ==================== PLAYLIST MUTATIONS ====================
        print("📝 Testing Playlist Mutations...")
        
        # Create a test playlist first
        print("  Creating test playlist...")
        try:
            result = playlists.create_playlist(
                self.client, 
                name=f"_MCP_TEST_{datetime.now().strftime('%H%M%S')}", 
                public=False,
                description="Temporary test playlist - will be deleted"
            )
            self.test_playlist_id = result["playlist"]["id"]
            self.results.append(MutationTestResult(
                tool_name="create_playlist",
                category="Playlists",
                status="WORKING"
            ))
            print(f"  ✅ create_playlist (created: {self.test_playlist_id})")
        except Exception as e:
            self.results.append(MutationTestResult(
                tool_name="create_playlist",
                category="Playlists",
                status="ERROR",
                error_message=str(e)
            ))
            print(f"  ❌ create_playlist - {e}")
            # Can't proceed with other playlist tests
            self.test_playlist_id = None
        
        if self.test_playlist_id:
            # Test add_tracks_to_playlist
            self.results.append(self.test_mutation(
                "add_tracks_to_playlist", "Playlists",
                lambda: playlists.add_tracks_to_playlist(
                    self.client, 
                    playlist_id=self.test_playlist_id,
                    track_uris=[self.SAMPLE_TRACK_URI]
                )
            ))
            
            # Test change_playlist_details
            self.results.append(self.test_mutation(
                "change_playlist_details", "Playlists",
                lambda: playlists.change_playlist_details(
                    self.client,
                    playlist_id=self.test_playlist_id,
                    description="Updated description"
                )
            ))
            
            # Test update_playlist_items (reorder) - need at least 2 tracks
            playlists.add_tracks_to_playlist(
                self.client, 
                playlist_id=self.test_playlist_id,
                track_uris=["spotify:track:0VjIjW4GlUZAMYd2vXMi3b"]  # Blinding Lights
            )
            self.results.append(self.test_mutation(
                "update_playlist_items", "Playlists",
                lambda: playlists.update_playlist_items(
                    self.client,
                    playlist_id=self.test_playlist_id,
                    range_start=0,
                    insert_before=2
                )
            ))
            
            # Test remove_tracks_from_playlist
            self.results.append(self.test_mutation(
                "remove_tracks_from_playlist", "Playlists",
                lambda: playlists.remove_tracks_from_playlist(
                    self.client,
                    playlist_id=self.test_playlist_id,
                    track_uris=[self.SAMPLE_TRACK_URI]
                )
            ))
            
            # Test follow_playlist (follow our own test playlist)
            self.results.append(self.test_mutation(
                "follow_playlist", "Playlists",
                lambda: playlists.follow_playlist(
                    self.client,
                    playlist_id=self.test_playlist_id
                )
            ))
            
            # Test unfollow_playlist
            self.results.append(self.test_mutation(
                "unfollow_playlist", "Playlists",
                lambda: playlists.unfollow_playlist(
                    self.client,
                    playlist_id=self.test_playlist_id
                )
            ))
            
            # Test add_custom_playlist_cover_image using the webp file
            try:
                from PIL import Image
                import io
                import base64
                
                # Load the webp image and convert to JPEG
                image_path = Path(__file__).parent / "playlist_cover.webp"
                if image_path.exists():
                    with Image.open(image_path) as img:
                        # Convert to RGB (JPEG doesn't support alpha)
                        if img.mode in ('RGBA', 'LA', 'P'):
                            img = img.convert('RGB')
                        # Resize to reasonable size (256KB limit for Spotify)
                        img.thumbnail((300, 300))
                        # Save to buffer as JPEG
                        buffer = io.BytesIO()
                        img.save(buffer, format='JPEG', quality=85)
                        image_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    
                    self.results.append(self.test_mutation(
                        "add_custom_playlist_cover_image", "Playlists",
                        lambda: playlists.add_custom_playlist_cover_image(
                            self.client,
                            playlist_id=self.test_playlist_id,
                            image_base64=image_b64
                        )
                    ))
                else:
                    print(f"  ⏭️ add_custom_playlist_cover_image - Skipped (no image file)")
                    self.results.append(MutationTestResult(
                        tool_name="add_custom_playlist_cover_image",
                        category="Playlists",
                        status="SKIPPED",
                        notes="No playlist_cover.webp file found"
                    ))
            except ImportError:
                print(f"  ⏭️ add_custom_playlist_cover_image - Skipped (Pillow not installed)")
                self.results.append(MutationTestResult(
                    tool_name="add_custom_playlist_cover_image",
                    category="Playlists",
                    status="SKIPPED",
                    notes="Pillow not installed for image conversion"
                ))
        
        # ==================== LIBRARY - TRACKS ====================
        print("\n📚 Testing Library Mutations (Tracks)...")
        
        # Check if track is already saved
        check_result = library.check_saved_tracks(self.client, track_ids=[self.SAMPLE_TRACK_ID])
        was_saved = check_result["tracks"][0]["is_saved"]
        
        # Test save_tracks
        self.results.append(self.test_mutation(
            "save_tracks", "Library",
            lambda: library.save_tracks(self.client, track_ids=[self.SAMPLE_TRACK_ID]),
            cleanup_func=lambda: library.remove_saved_tracks(self.client, track_ids=[self.SAMPLE_TRACK_ID]) if not was_saved else None
        ))
        
        # Test remove_saved_tracks (remove what we just added, or add then remove)
        if not was_saved:
            # We just added it, now remove it
            self.results.append(self.test_mutation(
                "remove_saved_tracks", "Library",
                lambda: library.remove_saved_tracks(self.client, track_ids=[self.SAMPLE_TRACK_ID])
            ))
        else:
            # It was already saved, test by removing and re-adding
            self.results.append(self.test_mutation(
                "remove_saved_tracks", "Library",
                lambda: library.remove_saved_tracks(self.client, track_ids=[self.SAMPLE_TRACK_ID]),
                cleanup_func=lambda: library.save_tracks(self.client, track_ids=[self.SAMPLE_TRACK_ID])
            ))
        
        # ==================== LIBRARY - ALBUMS ====================
        print("\n💿 Testing Library Mutations (Albums)...")
        
        check_result = albums.check_saved_albums(self.client, album_ids=[self.SAMPLE_ALBUM_ID])
        was_saved = check_result["albums"][0]["is_saved"]
        
        self.results.append(self.test_mutation(
            "save_albums", "Albums",
            lambda: albums.save_albums(self.client, album_ids=[self.SAMPLE_ALBUM_ID]),
            cleanup_func=lambda: albums.remove_saved_albums(self.client, album_ids=[self.SAMPLE_ALBUM_ID]) if not was_saved else None
        ))
        
        if not was_saved:
            self.results.append(self.test_mutation(
                "remove_saved_albums", "Albums",
                lambda: albums.remove_saved_albums(self.client, album_ids=[self.SAMPLE_ALBUM_ID])
            ))
        else:
            self.results.append(self.test_mutation(
                "remove_saved_albums", "Albums",
                lambda: albums.remove_saved_albums(self.client, album_ids=[self.SAMPLE_ALBUM_ID]),
                cleanup_func=lambda: albums.save_albums(self.client, album_ids=[self.SAMPLE_ALBUM_ID])
            ))
        
        # ==================== LIBRARY - SHOWS ====================
        print("\n📻 Testing Library Mutations (Shows)...")
        
        check_result = shows.check_saved_shows(self.client, show_ids=[self.SAMPLE_SHOW_ID])
        was_saved = check_result["shows"][0]["is_saved"]
        
        self.results.append(self.test_mutation(
            "save_shows", "Shows",
            lambda: shows.save_shows(self.client, show_ids=[self.SAMPLE_SHOW_ID]),
            cleanup_func=lambda: shows.remove_saved_shows(self.client, show_ids=[self.SAMPLE_SHOW_ID]) if not was_saved else None
        ))
        
        if not was_saved:
            self.results.append(self.test_mutation(
                "remove_saved_shows", "Shows",
                lambda: shows.remove_saved_shows(self.client, show_ids=[self.SAMPLE_SHOW_ID])
            ))
        else:
            self.results.append(self.test_mutation(
                "remove_saved_shows", "Shows",
                lambda: shows.remove_saved_shows(self.client, show_ids=[self.SAMPLE_SHOW_ID]),
                cleanup_func=lambda: shows.save_shows(self.client, show_ids=[self.SAMPLE_SHOW_ID])
            ))
        
        # ==================== LIBRARY - EPISODES ====================
        print("\n🎙️ Testing Library Mutations (Episodes)...")
        
        # First try to get a valid episode from a show
        try:
            show_eps = shows.get_show_episodes(self.client, show_id=self.SAMPLE_SHOW_ID, limit=1)
            if show_eps["episodes"]:
                test_episode_id = show_eps["episodes"][0]["id"]
            else:
                test_episode_id = self.SAMPLE_EPISODE_ID
        except:
            test_episode_id = self.SAMPLE_EPISODE_ID
        
        try:
            check_result = episodes.check_saved_episodes(self.client, episode_ids=[test_episode_id])
            was_saved = check_result["results"][0]["is_saved"]
            
            self.results.append(self.test_mutation(
                "save_episodes", "Episodes",
                lambda: episodes.save_episodes(self.client, episode_ids=[test_episode_id]),
                cleanup_func=lambda: episodes.remove_saved_episodes(self.client, episode_ids=[test_episode_id]) if not was_saved else None
            ))
            
            if not was_saved:
                self.results.append(self.test_mutation(
                    "remove_saved_episodes", "Episodes",
                    lambda: episodes.remove_saved_episodes(self.client, episode_ids=[test_episode_id])
                ))
            else:
                self.results.append(self.test_mutation(
                    "remove_saved_episodes", "Episodes",
                    lambda: episodes.remove_saved_episodes(self.client, episode_ids=[test_episode_id]),
                    cleanup_func=lambda: episodes.save_episodes(self.client, episode_ids=[test_episode_id])
                ))
        except Exception as e:
            print(f"  ⚠️ Episode test skipped: {e}")
            self.results.append(MutationTestResult(
                tool_name="save_episodes",
                category="Episodes",
                status="SKIPPED",
                notes=f"Could not test: {str(e)[:50]}"
            ))
            self.results.append(MutationTestResult(
                tool_name="remove_saved_episodes",
                category="Episodes",
                status="SKIPPED",
                notes=f"Could not test: {str(e)[:50]}"
            ))
        
        # ==================== USER - FOLLOW ====================
        print("\n👤 Testing User Follow Mutations...")
        
        # Test follow_artists_or_users (follow an artist)
        try:
            check = user.check_following_artists_or_users(
                self.client, ids=[self.SAMPLE_ARTIST_ID], follow_type="artist"
            )
            was_following = check["following"][0]["is_following"]
        except:
            was_following = False
        
        self.results.append(self.test_mutation(
            "follow_artists_or_users", "User",
            lambda: user.follow_artists_or_users(
                self.client, ids=[self.SAMPLE_ARTIST_ID], follow_type="artist"
            ),
            cleanup_func=lambda: user.unfollow_artists_or_users(
                self.client, ids=[self.SAMPLE_ARTIST_ID], follow_type="artist"
            ) if not was_following else None
        ))
        
        if not was_following:
            self.results.append(self.test_mutation(
                "unfollow_artists_or_users", "User",
                lambda: user.unfollow_artists_or_users(
                    self.client, ids=[self.SAMPLE_ARTIST_ID], follow_type="artist"
                )
            ))
        else:
            self.results.append(self.test_mutation(
                "unfollow_artists_or_users", "User",
                lambda: user.unfollow_artists_or_users(
                    self.client, ids=[self.SAMPLE_ARTIST_ID], follow_type="artist"
                ),
                cleanup_func=lambda: user.follow_artists_or_users(
                    self.client, ids=[self.SAMPLE_ARTIST_ID], follow_type="artist"
                )
            ))
        
        # ==================== QUEUE ====================
        print("\n📋 Testing Queue Mutations...")
        
        self.results.append(self.test_mutation(
            "add_to_queue", "Queue",
            lambda: queue.add_to_queue(self.client, uri=self.SAMPLE_TRACK_URI),
            notes="Requires active playback device"
        ))
        
        # ==================== PLAYBACK ====================
        print("\n🎵 Testing Playback Mutations...")
        print("  ⚠️ These require Spotify Premium + active device")
        
        # Test if we have an active device
        try:
            devices = playback.get_available_devices(self.client)
            has_device = len(devices.get("devices", [])) > 0
            active_device = any(d.get("is_active") for d in devices.get("devices", []))
        except:
            has_device = False
            active_device = False
        
        if not has_device:
            print("  ⚠️ No devices available - skipping playback tests")
            for tool in ["play", "pause", "skip_next", "skip_previous", 
                        "set_volume", "set_shuffle", "set_repeat", 
                        "seek_to_position", "transfer_playback"]:
                self.results.append(MutationTestResult(
                    tool_name=tool,
                    category="Playback",
                    status="SKIPPED",
                    notes="No active device available"
                ))
        else:
            # Try each playback operation
            playback_ops = [
                ("pause", lambda: playback.pause(self.client)),
                ("play", lambda: playback.play(self.client)),
                ("set_volume", lambda: playback.set_volume(self.client, volume_percent=50)),
                ("set_shuffle", lambda: playback.set_shuffle(self.client, state=False)),
                ("set_repeat", lambda: playback.set_repeat(self.client, state="off")),
                ("seek_to_position", lambda: playback.seek_to_position(self.client, position_ms=0)),
                ("skip_next", lambda: playback.skip_next(self.client)),
                ("skip_previous", lambda: playback.skip_previous(self.client)),
            ]
            
            for name, func in playback_ops:
                self.results.append(self.test_mutation(
                    name, "Playback", func,
                    notes="Requires Premium + active device"
                ))
            
            # Transfer playback needs specific device handling
            if len(devices.get("devices", [])) > 0:
                device_id = devices["devices"][0]["id"]
                self.results.append(self.test_mutation(
                    "transfer_playback", "Playback",
                    lambda: playback.transfer_playback(self.client, device_id=device_id),
                    notes="Requires Premium + multiple devices ideally"
                ))
            else:
                self.results.append(MutationTestResult(
                    tool_name="transfer_playback",
                    category="Playback",
                    status="SKIPPED",
                    notes="No device to transfer to"
                ))
        
        # ==================== AUDIOBOOKS ====================
        print("\n📖 Testing Audiobook Mutations...")
        
        # These likely don't exist in spotipy
        self.results.append(self.test_mutation(
            "save_audiobooks", "Audiobooks",
            lambda: audiobooks.save_audiobooks(self.client, audiobook_ids=["7iHfbu1YPACw6oZPAFJtqe"])
        ))
        
        self.results.append(self.test_mutation(
            "remove_saved_audiobooks", "Audiobooks",
            lambda: audiobooks.remove_saved_audiobooks(self.client, audiobook_ids=["7iHfbu1YPACw6oZPAFJtqe"])
        ))
        
        # ==================== CLEANUP ====================
        print("\n🧹 Cleanup...")
        if self.test_playlist_id:
            try:
                # Delete test playlist by unfollowing it
                playlists.unfollow_playlist(self.client, playlist_id=self.test_playlist_id)
                print(f"  ✅ Deleted test playlist {self.test_playlist_id}")
            except Exception as e:
                print(f"  ⚠️ Could not delete test playlist: {e}")
        
        print("\n✅ All mutation tests complete!")
    
    def print_summary(self):
        """Print results summary."""
        working = [r for r in self.results if r.status == "WORKING"]
        restricted = [r for r in self.results if r.status == "RESTRICTED"]
        premium = [r for r in self.results if r.status == "PREMIUM_REQUIRED"]
        errors = [r for r in self.results if r.status == "ERROR"]
        not_impl = [r for r in self.results if r.status == "NOT_IMPLEMENTED"]
        skipped = [r for r in self.results if r.status == "SKIPPED"]
        
        print("\n" + "="*60)
        print("📊 MUTATION TEST RESULTS SUMMARY")
        print("="*60)
        
        print(f"\n✅ WORKING:           {len(working)}")
        print(f"🚫 RESTRICTED (403):  {len(restricted)}")
        print(f"💎 PREMIUM REQUIRED:  {len(premium)}")
        print(f"🔧 NOT IN SPOTIPY:    {len(not_impl)}")
        print(f"❌ ERRORS:            {len(errors)}")
        print(f"⏭️  SKIPPED:           {len(skipped)}")
        print(f"{'─'*30}")
        print(f"📦 TOTAL:             {len(self.results)}")
        
        if working:
            print("\n✅ WORKING MUTATIONS:")
            for r in working:
                print(f"   - {r.tool_name} ({r.category})")
        
        if premium:
            print("\n💎 PREMIUM REQUIRED:")
            for r in premium:
                print(f"   - {r.tool_name}")
        
        if restricted:
            print("\n🚫 RESTRICTED:")
            for r in restricted:
                print(f"   - {r.tool_name}")
        
        if not_impl:
            print("\n🔧 NOT IN SPOTIPY:")
            for r in not_impl:
                print(f"   - {r.tool_name}")
        
        if errors:
            print("\n❌ ERRORS:")
            for r in errors:
                print(f"   - {r.tool_name}: {r.error_message[:50]}...")
        
        return {
            "working": len(working),
            "restricted": len(restricted),
            "premium": len(premium),
            "not_implemented": len(not_impl),
            "errors": len(errors),
            "skipped": len(skipped)
        }


def main():
    """Main entry point."""
    print("⚠️  WARNING: This test will:")
    print("   - Create a temporary playlist (and delete it)")
    print("   - Temporarily add/remove items from your library")
    print("   - Attempt playback operations if you have Premium")
    print("\nAll changes will be cleaned up after testing.\n")
    
    tester = MutationTester()
    
    if not tester.setup():
        print("\n❌ Cannot proceed without authentication.")
        sys.exit(1)
    
    tester.run_all_tests()
    summary = tester.print_summary()
    
    # Save results
    import json
    results_path = Path(__file__).parent / "mutation_test_results.json"
    with open(results_path, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "results": [
                {
                    "tool_name": r.tool_name,
                    "category": r.category,
                    "status": r.status,
                    "error_message": r.error_message,
                    "notes": r.notes
                }
                for r in tester.results
            ]
        }, f, indent=2)
    print(f"\n📊 Results saved to: {results_path}")


if __name__ == "__main__":
    main()
