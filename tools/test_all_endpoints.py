"""
Comprehensive Spotify API Endpoint Tester

This script systematically tests all 86 MCP tools against the Spotify API
to identify which endpoints work in Development Mode (without Extended Quota).

It generates a detailed report categorizing tools as:
- WORKING: Endpoint works fine
- RESTRICTED (403): Endpoint blocked by quota/permissions
- PREMIUM_REQUIRED: Needs Spotify Premium
- ERROR: Other errors (usually solvable)

Usage:
    python tools/test_all_endpoints.py

Output:
    - Console summary
    - tools/ENDPOINT_TEST_REPORT.md (detailed report)
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@dataclass
class TestResult:
    """Result of a single endpoint test."""
    tool_name: str
    category: str
    status: str  # WORKING, RESTRICTED, PREMIUM_REQUIRED, ERROR, SKIPPED
    http_status: int = 0
    error_message: str = ""
    response_preview: str = ""
    notes: str = ""


@dataclass
class TestReport:
    """Full test report."""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    results: List[TestResult] = field(default_factory=list)
    
    @property
    def working(self) -> List[TestResult]:
        return [r for r in self.results if r.status == "WORKING"]
    
    @property
    def restricted(self) -> List[TestResult]:
        return [r for r in self.results if r.status == "RESTRICTED"]
    
    @property
    def premium_required(self) -> List[TestResult]:
        return [r for r in self.results if r.status == "PREMIUM_REQUIRED"]
    
    @property
    def errors(self) -> List[TestResult]:
        return [r for r in self.results if r.status == "ERROR"]
    
    @property
    def skipped(self) -> List[TestResult]:
        return [r for r in self.results if r.status == "SKIPPED"]


class EndpointTester:
    """Tests all Spotify API endpoints."""
    
    # Sample data for testing (using real Spotify IDs)
    SAMPLE_DATA = {
        "track_id": "4iV5W9uYEdYUVa79Axb7Rh",  # Hotline Bling
        "track_ids": ["4iV5W9uYEdYUVa79Axb7Rh", "0VjIjW4GlUZAMYd2vXMi3b"],
        "album_id": "4aawyAB9vmqN3uQ7FjRGTy",  # Global Warming
        "album_ids": ["4aawyAB9vmqN3uQ7FjRGTy", "2noRn2Aes5aoNVsU6iWThc"],
        "artist_id": "3TVXtAsR1Inumwj472S9r4",  # Drake
        "artist_ids": ["3TVXtAsR1Inumwj472S9r4", "06HL4z0CvFAxyc27GXpf02"],
        "playlist_id": "37i9dQZF1DXcBWIGoYBM5M",  # Today's Top Hits
        "audiobook_id": "7iHfbu1YPACw6oZPAFJtqe",  # Sample audiobook
        "audiobook_ids": ["7iHfbu1YPACw6oZPAFJtqe"],
        "chapter_id": "0D5wENdkdwbqlrHoaJ9g29",  # Sample chapter
        "chapter_ids": ["0D5wENdkdwbqlrHoaJ9g29"],
        "show_id": "5CfCWKI5pZ28U0uOzXkDHe",  # TED Talks Daily
        "show_ids": ["5CfCWKI5pZ28U0uOzXkDHe"],
        "episode_id": "512ojhOuo1ktJprKbVcKyQ",  # Sample episode
        "episode_ids": ["512ojhOuo1ktJprKbVcKyQ"],
        "category_id": "toplists",
        "user_id": "spotify",
        "market": "US",
    }
    
    def __init__(self):
        self.report = TestReport()
        self.client = None
        self.user_id = None
        
    def setup(self):
        """Initialize Spotify client."""
        print("🔐 Authenticating with Spotify...")
        try:
            from spotify_mcp.auth import get_spotify_client
            from spotify_mcp.spotify_client import SpotifyClient
            
            sp = get_spotify_client()
            self.client = SpotifyClient(sp)
            
            # Get current user for tests that need it
            user = self.client.current_user()
            self.user_id = user.get("id")
            print(f"✅ Authenticated as: {user.get('display_name', 'Unknown')} ({self.user_id})")
            
            # Get user's first playlist for testing
            playlists = self.client.current_user_playlists(limit=1)
            if playlists.get("items"):
                self.user_playlist_id = playlists["items"][0]["id"]
            else:
                self.user_playlist_id = None
            
            return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    def _get_user_playlist_id(self):
        """Get user's own playlist ID for testing."""
        return self.user_playlist_id or self.SAMPLE_DATA["playlist_id"]
    
    def test_endpoint(self, tool_name: str, category: str, 
                     test_func, notes: str = "") -> TestResult:
        """Test a single endpoint and categorize the result."""
        result = TestResult(
            tool_name=tool_name,
            category=category,
            status="UNKNOWN",
            notes=notes
        )
        
        try:
            response = test_func()
            result.status = "WORKING"
            
            # Capture response preview
            if isinstance(response, dict):
                preview = json.dumps(response, indent=2)[:200]
                result.response_preview = preview + "..." if len(preview) >= 200 else preview
            else:
                result.response_preview = str(response)[:200]
                
        except Exception as e:
            error_str = str(e)
            
            # Categorize the error
            if "403" in error_str or "Forbidden" in error_str.lower():
                if "PREMIUM_REQUIRED" in error_str:
                    result.status = "PREMIUM_REQUIRED"
                else:
                    result.status = "RESTRICTED"
                result.http_status = 403
            elif "401" in error_str or "Unauthorized" in error_str.lower():
                result.status = "ERROR"
                result.http_status = 401
            elif "404" in error_str or "Not found" in error_str.lower():
                result.status = "ERROR"
                result.http_status = 404
            elif "400" in error_str or "Bad request" in error_str.lower():
                result.status = "ERROR"  
                result.http_status = 400
            else:
                result.status = "ERROR"
                
            result.error_message = error_str
        
        # Rate limiting protection
        time.sleep(0.3)
        
        return result
    
    def run_all_tests(self):
        """Run all endpoint tests."""
        
        # Import tools
        from spotify_mcp.tools import playback, search, library, albums, playlists
        from spotify_mcp.tools import queue, user, artists, audiobooks, categories
        from spotify_mcp.tools import chapters, episodes, genres, markets, shows, tracks
        
        print("\n" + "="*60)
        print("🧪 SPOTIFY API ENDPOINT TESTING")
        print("="*60 + "\n")
        
        # ==================== PLAYBACK TOOLS ====================
        print("📀 Testing Playback Tools...")
        
        self.report.results.append(self.test_endpoint(
            "get_current_playback", "Playback",
            lambda: playback.get_current_playback(self.client),
            "May return empty if nothing playing"
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_available_devices", "Playback",
            lambda: playback.get_available_devices(self.client),
            "Returns list of devices"
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_recently_played", "Playback",
            lambda: playback.get_recently_played(self.client, limit=5),
            "Last played tracks"
        ))
        
        # Mutation playback tests - SKIPPED to avoid disrupting playback
        for tool in ["play", "pause", "skip_next", "skip_previous", 
                    "set_volume", "set_shuffle", "set_repeat", 
                    "seek_to_position", "transfer_playback"]:
            self.report.results.append(TestResult(
                tool_name=tool,
                category="Playback",
                status="SKIPPED",
                notes="Skipped: Would modify playback state. Requires active device + Premium."
            ))
        
        # ==================== SEARCH TOOLS ====================
        print("🔍 Testing Search Tools...")
        
        self.report.results.append(self.test_endpoint(
            "search", "Search",
            lambda: search.search(self.client, query="test", search_type="track", limit=5)
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_recommendations", "Search",
            lambda: search.get_recommendations(
                self.client, 
                seed_tracks=[self.SAMPLE_DATA["track_id"]],
                limit=5
            ),
            "Personalized recommendations - may be restricted"
        ))
        
        # ==================== LIBRARY TOOLS ====================
        print("📚 Testing Library Tools...")
        
        self.report.results.append(self.test_endpoint(
            "get_saved_tracks", "Library",
            lambda: library.get_saved_tracks(self.client, limit=5)
        ))
        
        self.report.results.append(self.test_endpoint(
            "check_saved_tracks", "Library",
            lambda: library.check_saved_tracks(self.client, track_ids=self.SAMPLE_DATA["track_ids"])
        ))
        
        # Skip mutation tests
        for tool in ["save_tracks", "remove_saved_tracks"]:
            self.report.results.append(TestResult(
                tool_name=tool,
                category="Library",
                status="SKIPPED",
                notes="Skipped: Would modify library. Likely works if read operations work."
            ))
        
        # ==================== ALBUM TOOLS ====================
        print("💿 Testing Album Tools...")
        
        self.report.results.append(self.test_endpoint(
            "get_album", "Albums",
            lambda: albums.get_album(self.client, album_id=self.SAMPLE_DATA["album_id"])
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_several_albums", "Albums",
            lambda: albums.get_several_albums(self.client, album_ids=self.SAMPLE_DATA["album_ids"])
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_album_tracks", "Albums",
            lambda: albums.get_album_tracks(self.client, album_id=self.SAMPLE_DATA["album_id"], limit=5)
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_saved_albums", "Albums",
            lambda: albums.get_saved_albums(self.client, limit=5)
        ))
        
        self.report.results.append(self.test_endpoint(
            "check_saved_albums", "Albums",
            lambda: albums.check_saved_albums(self.client, album_ids=self.SAMPLE_DATA["album_ids"])
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_new_releases", "Albums",
            lambda: albums.get_new_releases(self.client, limit=5)
        ))
        
        for tool in ["save_albums", "remove_saved_albums"]:
            self.report.results.append(TestResult(
                tool_name=tool,
                category="Albums",
                status="SKIPPED",
                notes="Skipped: Would modify library."
            ))
        
        # ==================== ARTIST TOOLS ====================
        print("🎤 Testing Artist Tools...")
        
        self.report.results.append(self.test_endpoint(
            "get_artist", "Artists",
            lambda: artists.get_artist(self.client, artist_id=self.SAMPLE_DATA["artist_id"])
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_several_artists", "Artists",
            lambda: artists.get_several_artists(self.client, artist_ids=self.SAMPLE_DATA["artist_ids"])
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_artist_albums", "Artists",
            lambda: artists.get_artist_albums(self.client, artist_id=self.SAMPLE_DATA["artist_id"], limit=5)
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_artist_top_tracks", "Artists",
            lambda: artists.get_artist_top_tracks(self.client, artist_id=self.SAMPLE_DATA["artist_id"])
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_artist_related_artists", "Artists",
            lambda: artists.get_artist_related_artists(self.client, artist_id=self.SAMPLE_DATA["artist_id"])
        ))
        
        # ==================== PLAYLIST TOOLS ====================
        print("📝 Testing Playlist Tools...")
        
        self.report.results.append(self.test_endpoint(
            "get_user_playlists", "Playlists",
            lambda: playlists.get_user_playlists(self.client, limit=5)
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_playlist", "Playlists",
            lambda: playlists.get_playlist(self.client, playlist_id=self._get_user_playlist_id()),
            "Testing with user's own playlist"
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_featured_playlists", "Playlists",
            lambda: playlists.get_featured_playlists(self.client, limit=5)
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_category_playlists", "Playlists",
            lambda: playlists.get_category_playlists(self.client, category_id=self.SAMPLE_DATA["category_id"], limit=5)
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_playlist_cover_image", "Playlists",
            lambda: playlists.get_playlist_cover_image(self.client, playlist_id=self.SAMPLE_DATA["playlist_id"])
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_user_playlists_by_id", "Playlists",
            lambda: playlists.get_user_playlists_by_id(self.client, user_id="spotify", limit=5)
        ))
        
        # Skip mutation tests
        for tool in ["create_playlist", "add_tracks_to_playlist", "remove_tracks_from_playlist",
                    "change_playlist_details", "update_playlist_items", 
                    "add_custom_playlist_cover_image", "follow_playlist", "unfollow_playlist"]:
            self.report.results.append(TestResult(
                tool_name=tool,
                category="Playlists",
                status="SKIPPED",
                notes="Skipped: Would modify playlists."
            ))
        
        # ==================== QUEUE TOOLS ====================
        print("📋 Testing Queue Tools...")
        
        self.report.results.append(self.test_endpoint(
            "get_queue", "Queue",
            lambda: queue.get_queue(self.client),
            "Requires active playback"
        ))
        
        self.report.results.append(TestResult(
            tool_name="add_to_queue",
            category="Queue",
            status="SKIPPED",
            notes="Skipped: Would modify queue."
        ))
        
        # ==================== USER TOOLS ====================
        print("👤 Testing User Tools...")
        
        self.report.results.append(self.test_endpoint(
            "get_current_user", "User",
            lambda: user.get_current_user(self.client)
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_top_items", "User",
            lambda: user.get_top_items(self.client, item_type="tracks", limit=5),
            "Top tracks/artists - may be restricted"
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_user_profile", "User",
            lambda: user.get_user_profile(self.client, user_id="spotify")
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_followed_artists", "User",
            lambda: user.get_followed_artists(self.client, limit=5)
        ))
        
        self.report.results.append(self.test_endpoint(
            "check_following_artists_or_users", "User",
            lambda: user.check_following_artists_or_users(
                self.client, 
                ids=[self.SAMPLE_DATA["artist_id"]], 
                follow_type="artist"
            )
        ))
        
        self.report.results.append(self.test_endpoint(
            "check_current_user_follows_playlist", "User",
            lambda: user.check_current_user_follows_playlist(
                self.client,
                playlist_id=self.SAMPLE_DATA["playlist_id"],
                user_ids=[self.user_id] if self.user_id else ["spotify"]
            )
        ))
        
        for tool in ["follow_artists_or_users", "unfollow_artists_or_users"]:
            self.report.results.append(TestResult(
                tool_name=tool,
                category="User",
                status="SKIPPED",
                notes="Skipped: Would modify following list."
            ))
        
        # ==================== AUDIOBOOK TOOLS ====================
        print("📖 Testing Audiobook Tools...")
        
        self.report.results.append(self.test_endpoint(
            "get_audiobook", "Audiobooks",
            lambda: audiobooks.get_audiobook(self.client, audiobook_id=self.SAMPLE_DATA["audiobook_id"]),
            "Audiobook API - likely restricted"
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_several_audiobooks", "Audiobooks",
            lambda: audiobooks.get_several_audiobooks(self.client, audiobook_ids=self.SAMPLE_DATA["audiobook_ids"]),
            "Audiobook API - likely restricted"
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_audiobook_chapters", "Audiobooks",
            lambda: audiobooks.get_audiobook_chapters(self.client, audiobook_id=self.SAMPLE_DATA["audiobook_id"], limit=5),
            "Audiobook API - likely restricted"
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_saved_audiobooks", "Audiobooks",
            lambda: audiobooks.get_saved_audiobooks(self.client, limit=5),
            "Audiobook API - likely restricted"
        ))
        
        self.report.results.append(self.test_endpoint(
            "check_saved_audiobooks", "Audiobooks",
            lambda: audiobooks.check_saved_audiobooks(self.client, audiobook_ids=self.SAMPLE_DATA["audiobook_ids"]),
            "Audiobook API - likely restricted"
        ))
        
        for tool in ["save_audiobooks", "remove_saved_audiobooks"]:
            self.report.results.append(TestResult(
                tool_name=tool,
                category="Audiobooks",
                status="SKIPPED",
                notes="Skipped: Would modify library. Audiobook API likely restricted anyway."
            ))
        
        # ==================== CATEGORY TOOLS ====================
        print("🏷️ Testing Category Tools...")
        
        self.report.results.append(self.test_endpoint(
            "get_several_browse_categories", "Categories",
            lambda: categories.get_several_browse_categories(self.client, limit=5)
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_single_browse_category", "Categories",
            lambda: categories.get_single_browse_category(self.client, category_id=self.SAMPLE_DATA["category_id"])
        ))
        
        # ==================== CHAPTER TOOLS ====================
        print("📑 Testing Chapter Tools...")
        
        self.report.results.append(self.test_endpoint(
            "get_chapter", "Chapters",
            lambda: chapters.get_chapter(self.client, chapter_id=self.SAMPLE_DATA["chapter_id"]),
            "Chapter API - likely restricted"
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_several_chapters", "Chapters",
            lambda: chapters.get_several_chapters(self.client, chapter_ids=self.SAMPLE_DATA["chapter_ids"]),
            "Chapter API - likely restricted"
        ))
        
        # ==================== EPISODE TOOLS ====================
        print("🎙️ Testing Episode Tools...")
        
        self.report.results.append(self.test_endpoint(
            "get_episode", "Episodes",
            lambda: episodes.get_episode(self.client, episode_id=self.SAMPLE_DATA["episode_id"])
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_several_episodes", "Episodes",
            lambda: episodes.get_several_episodes(self.client, episode_ids=self.SAMPLE_DATA["episode_ids"])
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_saved_episodes", "Episodes",
            lambda: episodes.get_saved_episodes(self.client, limit=5)
        ))
        
        self.report.results.append(self.test_endpoint(
            "check_saved_episodes", "Episodes",
            lambda: episodes.check_saved_episodes(self.client, episode_ids=self.SAMPLE_DATA["episode_ids"])
        ))
        
        for tool in ["save_episodes", "remove_saved_episodes"]:
            self.report.results.append(TestResult(
                tool_name=tool,
                category="Episodes",
                status="SKIPPED",
                notes="Skipped: Would modify library."
            ))
        
        # ==================== GENRE TOOLS ====================
        print("🎸 Testing Genre Tools...")
        
        self.report.results.append(self.test_endpoint(
            "get_available_genre_seeds", "Genres",
            lambda: genres.get_available_genre_seeds(self.client)
        ))
        
        # ==================== MARKET TOOLS ====================
        print("🌍 Testing Market Tools...")
        
        self.report.results.append(self.test_endpoint(
            "get_available_markets", "Markets",
            lambda: markets.get_available_markets(self.client)
        ))
        
        # ==================== SHOW TOOLS ====================
        print("📻 Testing Show Tools...")
        
        self.report.results.append(self.test_endpoint(
            "get_show", "Shows",
            lambda: shows.get_show(self.client, show_id=self.SAMPLE_DATA["show_id"])
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_several_shows", "Shows",
            lambda: shows.get_several_shows(self.client, show_ids=self.SAMPLE_DATA["show_ids"])
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_show_episodes", "Shows",
            lambda: shows.get_show_episodes(self.client, show_id=self.SAMPLE_DATA["show_id"], limit=5)
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_saved_shows", "Shows",
            lambda: shows.get_saved_shows(self.client, limit=5)
        ))
        
        self.report.results.append(self.test_endpoint(
            "check_saved_shows", "Shows",
            lambda: shows.check_saved_shows(self.client, show_ids=self.SAMPLE_DATA["show_ids"])
        ))
        
        for tool in ["save_shows", "remove_saved_shows"]:
            self.report.results.append(TestResult(
                tool_name=tool,
                category="Shows",
                status="SKIPPED",
                notes="Skipped: Would modify library."
            ))
        
        # ==================== TRACK TOOLS ====================
        print("🎵 Testing Track Tools...")
        
        self.report.results.append(self.test_endpoint(
            "get_track", "Tracks",
            lambda: tracks.get_track(self.client, track_id=self.SAMPLE_DATA["track_id"])
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_several_tracks", "Tracks",
            lambda: tracks.get_several_tracks(self.client, track_ids=self.SAMPLE_DATA["track_ids"])
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_track_audio_features", "Tracks",
            lambda: tracks.get_track_audio_features(self.client, track_id=self.SAMPLE_DATA["track_id"]),
            "Audio Features API - likely restricted"
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_tracks_audio_features", "Tracks",
            lambda: tracks.get_tracks_audio_features(self.client, track_ids=self.SAMPLE_DATA["track_ids"]),
            "Audio Features API - likely restricted"
        ))
        
        self.report.results.append(self.test_endpoint(
            "get_track_audio_analysis", "Tracks",
            lambda: tracks.get_track_audio_analysis(self.client, track_id=self.SAMPLE_DATA["track_id"]),
            "Audio Analysis API - likely restricted"
        ))
        
        print("\n✅ All tests complete!")
    
    def generate_report(self) -> str:
        """Generate markdown report."""
        lines = [
            "# Spotify API Endpoint Test Report",
            "",
            f"**Generated:** {self.report.timestamp}",
            "",
            "## Summary",
            "",
            f"| Status | Count |",
            f"|--------|-------|",
            f"| ✅ WORKING | {len(self.report.working)} |",
            f"| 🚫 RESTRICTED (403) | {len(self.report.restricted)} |",
            f"| 💎 PREMIUM_REQUIRED | {len(self.report.premium_required)} |",
            f"| ❌ ERROR | {len(self.report.errors)} |",
            f"| ⏭️ SKIPPED | {len(self.report.skipped)} |",
            f"| **TOTAL** | **{len(self.report.results)}** |",
            "",
        ]
        
        # Working endpoints
        lines.extend([
            "## ✅ Working Endpoints",
            "",
            "These endpoints work fine in Development Mode:",
            "",
            "| Tool | Category | Notes |",
            "|------|----------|-------|",
        ])
        for r in sorted(self.report.working, key=lambda x: x.category):
            lines.append(f"| `{r.tool_name}` | {r.category} | {r.notes} |")
        
        # Restricted endpoints
        lines.extend([
            "",
            "## 🚫 Restricted Endpoints (403 Forbidden)",
            "",
            "These endpoints require Extended Quota Mode or are unavailable:",
            "",
            "| Tool | Category | Error | Notes |",
            "|------|----------|-------|-------|",
        ])
        for r in sorted(self.report.restricted, key=lambda x: x.category):
            error_short = r.error_message[:100] + "..." if len(r.error_message) > 100 else r.error_message
            lines.append(f"| `{r.tool_name}` | {r.category} | {error_short} | {r.notes} |")
        
        # Premium required
        if self.report.premium_required:
            lines.extend([
                "",
                "## 💎 Premium Required",
                "",
                "These endpoints require Spotify Premium:",
                "",
                "| Tool | Category | Notes |",
                "|------|----------|-------|",
            ])
            for r in sorted(self.report.premium_required, key=lambda x: x.category):
                lines.append(f"| `{r.tool_name}` | {r.category} | {r.notes} |")
        
        # Errors
        if self.report.errors:
            lines.extend([
                "",
                "## ❌ Errors",
                "",
                "These endpoints had other errors (may be fixable):",
                "",
                "| Tool | Category | HTTP | Error |",
                "|------|----------|------|-------|",
            ])
            for r in sorted(self.report.errors, key=lambda x: x.category):
                error_short = r.error_message[:80] + "..." if len(r.error_message) > 80 else r.error_message
                lines.append(f"| `{r.tool_name}` | {r.category} | {r.http_status} | {error_short} |")
        
        # Skipped
        lines.extend([
            "",
            "## ⏭️ Skipped (Mutation Operations)",
            "",
            "These were skipped to avoid modifying your account:",
            "",
            "| Tool | Category | Notes |",
            "|------|----------|-------|",
        ])
        for r in sorted(self.report.skipped, key=lambda x: x.category):
            lines.append(f"| `{r.tool_name}` | {r.category} | {r.notes} |")
        
        # Recommendations
        lines.extend([
            "",
            "## 🎯 Recommendations",
            "",
            "### Keep (Working)",
            "```",
        ])
        for r in self.report.working:
            lines.append(f"- {r.tool_name}")
        lines.append("```")
        
        lines.extend([
            "",
            "### Remove or Disable (Restricted)",
            "```",
        ])
        for r in self.report.restricted:
            lines.append(f"- {r.tool_name}")
        lines.append("```")
        
        lines.extend([
            "",
            "### Investigate (Errors)",
            "```",
        ])
        for r in self.report.errors:
            lines.append(f"- {r.tool_name}: {r.error_message[:50]}...")
        lines.append("```")
        
        return "\n".join(lines)
    
    def print_summary(self):
        """Print summary to console."""
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        
        print(f"\n✅ WORKING:          {len(self.report.working)}")
        print(f"🚫 RESTRICTED (403): {len(self.report.restricted)}")
        print(f"💎 PREMIUM REQUIRED: {len(self.report.premium_required)}")
        print(f"❌ ERRORS:           {len(self.report.errors)}")
        print(f"⏭️  SKIPPED:          {len(self.report.skipped)}")
        print(f"{'─'*30}")
        print(f"📦 TOTAL:            {len(self.report.results)}")
        
        if self.report.restricted:
            print("\n🚫 RESTRICTED ENDPOINTS:")
            for r in self.report.restricted:
                print(f"   - {r.tool_name} ({r.category})")
        
        if self.report.errors:
            print("\n❌ ENDPOINTS WITH ERRORS:")
            for r in self.report.errors:
                print(f"   - {r.tool_name}: {r.error_message[:60]}...")


def main():
    """Main entry point."""
    tester = EndpointTester()
    
    if not tester.setup():
        print("\n❌ Cannot proceed without authentication.")
        sys.exit(1)
    
    tester.run_all_tests()
    tester.print_summary()
    
    # Save report
    report_path = Path(__file__).parent / "ENDPOINT_TEST_REPORT.md"
    report_content = tester.generate_report()
    report_path.write_text(report_content, encoding="utf-8")
    print(f"\n📝 Full report saved to: {report_path}")
    
    # Also save JSON for programmatic access
    json_path = Path(__file__).parent / "endpoint_test_results.json"
    json_data = {
        "timestamp": tester.report.timestamp,
        "summary": {
            "working": len(tester.report.working),
            "restricted": len(tester.report.restricted),
            "premium_required": len(tester.report.premium_required),
            "errors": len(tester.report.errors),
            "skipped": len(tester.report.skipped),
            "total": len(tester.report.results)
        },
        "results": [
            {
                "tool_name": r.tool_name,
                "category": r.category,
                "status": r.status,
                "http_status": r.http_status,
                "error_message": r.error_message,
                "notes": r.notes
            }
            for r in tester.report.results
        ]
    }
    json_path.write_text(json.dumps(json_data, indent=2), encoding="utf-8")
    print(f"📊 JSON results saved to: {json_path}")


if __name__ == "__main__":
    main()
