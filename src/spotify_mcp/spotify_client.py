"""
Spotify API client wrapper with error handling and convenience methods.
"""

import time
from typing import Optional, Dict, List, Any
import spotipy
from spotipy.exceptions import SpotifyException


class SpotifyClient:
    """Wrapper around spotipy.Spotify with enhanced error handling."""
    
    def __init__(self, sp: spotipy.Spotify):
        self.sp = sp
    
    def _handle_api_call(self, func, *args, **kwargs) -> Any:
        """
        Wrapper for API calls with error handling and retry logic.
        """
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except SpotifyException as e:
                # Rate limiting
                if e.http_status == 429:
                    retry_after = int(e.headers.get('Retry-After', retry_delay))
                    if attempt < max_retries - 1:
                        time.sleep(retry_after)
                        retry_delay *= 2
                        continue
                    raise Exception(f"Rate limited by Spotify API. Please try again in {retry_after} seconds.")
                
                # No active device
                elif e.http_status == 404 and "NO_ACTIVE_DEVICE" in str(e):
                    raise Exception(
                        "No active Spotify device found. Please open Spotify on any device "
                        "(phone, desktop, web player, etc.) to make it available for playback control."
                    )
                
                # Premium required
                elif e.http_status == 403 and "PREMIUM_REQUIRED" in str(e):
                    raise Exception(
                        "This operation requires Spotify Premium. Playback control features "
                        "are only available to Premium subscribers."
                    )
                
                # Bad request - usually invalid parameters
                elif e.http_status == 400:
                    raise Exception(f"Invalid request: {e.msg}")
                
                # Unauthorized - token issues
                elif e.http_status == 401:
                    raise Exception(
                        "Authentication failed. Your token may have expired. "
                        "Please restart the server to re-authenticate."
                    )
                
                # Not found
                elif e.http_status == 404:
                    raise Exception(f"Resource not found: {e.msg}")
                
                # Generic Spotify error
                else:
                    raise Exception(f"Spotify API error ({e.http_status}): {e.msg}")
            
            except Exception as e:
                if attempt < max_retries - 1 and "timeout" in str(e).lower():
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                raise
        
        raise Exception("Max retries exceeded")
    
    # Playback methods
    def start_playback(self, device_id: Optional[str] = None, context_uri: Optional[str] = None, 
                       uris: Optional[List[str]] = None, offset: Optional[Dict] = None):
        """Start or resume playback."""
        return self._handle_api_call(self.sp.start_playback, device_id=device_id, 
                                     context_uri=context_uri, uris=uris, offset=offset)
    
    def pause_playback(self, device_id: Optional[str] = None):
        """Pause playback."""
        return self._handle_api_call(self.sp.pause_playback, device_id=device_id)
    
    def next_track(self, device_id: Optional[str] = None):
        """Skip to next track."""
        return self._handle_api_call(self.sp.next_track, device_id=device_id)
    
    def previous_track(self, device_id: Optional[str] = None):
        """Skip to previous track."""
        return self._handle_api_call(self.sp.previous_track, device_id=device_id)
    
    def current_playback(self):
        """Get current playback state."""
        return self._handle_api_call(self.sp.current_playback)
    
    def devices(self):
        """Get available devices."""
        return self._handle_api_call(self.sp.devices)
    
    def transfer_playback(self, device_id: str, force_play: bool = False):
        """Transfer playback to a different device."""
        return self._handle_api_call(self.sp.transfer_playback, device_id=device_id, force_play=force_play)
    
    def volume(self, volume_percent: int, device_id: Optional[str] = None):
        """Set volume (0-100)."""
        return self._handle_api_call(self.sp.volume, volume_percent=volume_percent, device_id=device_id)
    
    def shuffle(self, state: bool, device_id: Optional[str] = None):
        """Set shuffle mode."""
        return self._handle_api_call(self.sp.shuffle, state=state, device_id=device_id)
    
    def repeat(self, state: str, device_id: Optional[str] = None):
        """Set repeat mode (track, context, off)."""
        return self._handle_api_call(self.sp.repeat, state=state, device_id=device_id)
    
    def seek_track(self, position_ms: int, device_id: Optional[str] = None):
        """Seek to position in current track."""
        return self._handle_api_call(self.sp.seek_track, position_ms=position_ms, device_id=device_id)
    
    # Search methods
    def search(self, q: str, limit: int = 20, offset: int = 0, type: str = "track"):
        """Search for tracks, albums, artists, or playlists."""
        return self._handle_api_call(self.sp.search, q=q, limit=limit, offset=offset, type=type)
    
    def recommendations(self, seed_artists: Optional[List[str]] = None, 
                       seed_tracks: Optional[List[str]] = None,
                       seed_genres: Optional[List[str]] = None, limit: int = 20, **kwargs):
        """Get recommendations based on seeds."""
        return self._handle_api_call(self.sp.recommendations, seed_artists=seed_artists,
                                     seed_tracks=seed_tracks, seed_genres=seed_genres, 
                                     limit=limit, **kwargs)
    
    # Library methods
    def current_user_saved_tracks(self, limit: int = 20, offset: int = 0):
        """Get user's saved tracks."""
        return self._handle_api_call(self.sp.current_user_saved_tracks, limit=limit, offset=offset)
    
    def current_user_saved_tracks_add(self, tracks: List[str]):
        """Save tracks to library."""
        return self._handle_api_call(self.sp.current_user_saved_tracks_add, tracks=tracks)
    
    def current_user_saved_tracks_delete(self, tracks: List[str]):
        """Remove tracks from library."""
        return self._handle_api_call(self.sp.current_user_saved_tracks_delete, tracks=tracks)
    
    def current_user_saved_tracks_contains(self, tracks: List[str]):
        """Check if tracks are saved."""
        return self._handle_api_call(self.sp.current_user_saved_tracks_contains, tracks=tracks)
    
    # Playlist methods
    def current_user_playlists(self, limit: int = 50, offset: int = 0):
        """Get user's playlists."""
        return self._handle_api_call(self.sp.current_user_playlists, limit=limit, offset=offset)
    
    def playlist(self, playlist_id: str):
        """Get playlist details."""
        return self._handle_api_call(self.sp.playlist, playlist_id=playlist_id)
    
    def playlist_items(self, playlist_id: str, limit: int = 100, offset: int = 0):
        """Get playlist tracks."""
        return self._handle_api_call(self.sp.playlist_items, playlist_id=playlist_id, 
                                     limit=limit, offset=offset)
    
    def user_playlist_create(self, user: str, name: str, public: bool = True, 
                            description: str = ""):
        """Create a playlist."""
        return self._handle_api_call(self.sp.user_playlist_create, user=user, name=name,
                                     public=public, description=description)
    
    def playlist_add_items(self, playlist_id: str, items: List[str]):
        """Add tracks to playlist."""
        return self._handle_api_call(self.sp.playlist_add_items, playlist_id=playlist_id, items=items)
    
    def playlist_remove_all_occurrences_of_items(self, playlist_id: str, items: List[str]):
        """Remove tracks from playlist."""
        return self._handle_api_call(self.sp.playlist_remove_all_occurrences_of_items, 
                                     playlist_id=playlist_id, items=items)
    
    # Queue methods
    def queue(self):
        """Get the current queue."""
        return self._handle_api_call(self.sp.queue)
    
    def add_to_queue(self, uri: str, device_id: Optional[str] = None):
        """Add track to queue."""
        return self._handle_api_call(self.sp.add_to_queue, uri=uri, device_id=device_id)
    
    # User methods
    def current_user(self):
        """Get current user's profile."""
        return self._handle_api_call(self.sp.current_user)
    
    def current_user_top_tracks(self, limit: int = 20, offset: int = 0, time_range: str = "medium_term"):
        """Get user's top tracks."""
        return self._handle_api_call(self.sp.current_user_top_tracks, limit=limit, 
                                     offset=offset, time_range=time_range)
    
    def current_user_top_artists(self, limit: int = 20, offset: int = 0, time_range: str = "medium_term"):
        """Get user's top artists."""
        return self._handle_api_call(self.sp.current_user_top_artists, limit=limit,
                                     offset=offset, time_range=time_range)
