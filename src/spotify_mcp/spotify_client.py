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
        Includes rate limiting protection and input sanitization.
        """
        max_retries = 3
        retry_delay = 1
        
        # Sanitize string inputs to prevent injection
        for key, value in list(kwargs.items()):
            if isinstance(value, str):
                # Remove any potentially dangerous characters
                kwargs[key] = value.replace('\x00', '').strip()
        
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
    
    def seek_track(self, position_ms: int, device_id: Optional[str] = None) -> None:
        """Seek to position in currently playing track."""
        kwargs = {"position_ms": position_ms}
        if device_id:
            kwargs["device_id"] = device_id
        self._handle_api_call(self.sp.seek_track, **kwargs)
    
    def current_user_recently_played(self, limit: int = 20, after: Optional[int] = None, 
                                     before: Optional[int] = None) -> Dict[str, Any]:
        """Get current user's recently played tracks."""
        kwargs = {"limit": limit}
        if after is not None:
            kwargs["after"] = after
        if before is not None:
            kwargs["before"] = before
        return self._handle_api_call(self.sp.current_user_recently_played, **kwargs)
    
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
    
    # Library methods - Tracks
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
    
    # Library methods - Albums
    def current_user_saved_albums(self, limit: int = 20, offset: int = 0):
        """Get user's saved albums."""
        return self._handle_api_call(self.sp.current_user_saved_albums, limit=limit, offset=offset)
    
    def current_user_saved_albums_add(self, albums: List[str]):
        """Save albums to library."""
        return self._handle_api_call(self.sp.current_user_saved_albums_add, albums=albums)
    
    def current_user_saved_albums_delete(self, albums: List[str]):
        """Remove albums from library."""
        return self._handle_api_call(self.sp.current_user_saved_albums_delete, albums=albums)
    
    def current_user_saved_albums_contains(self, albums: List[str]):
        """Check if albums are saved."""
        return self._handle_api_call(self.sp.current_user_saved_albums_contains, albums=albums)
    
    # Album catalog methods
    def album(self, album_id: str):
        """Get album information."""
        return self._handle_api_call(self.sp.album, album_id=album_id)
    
    def albums(self, album_ids: List[str]):
        """Get multiple albums."""
        return self._handle_api_call(self.sp.albums, albums=album_ids)
    
    def album_tracks(self, album_id: str, limit: int = 50, offset: int = 0):
        """Get album tracks."""
        return self._handle_api_call(self.sp.album_tracks, album_id=album_id, limit=limit, offset=offset)
    
    def new_releases(self, limit: int = 20, offset: int = 0, country: Optional[str] = None):
        """Get new album releases."""
        kwargs = {"limit": limit, "offset": offset}
        if country:
            kwargs["country"] = country
        return self._handle_api_call(self.sp.new_releases, **kwargs)
    
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
    
    def playlist_change_details(self, playlist_id: str, name: Optional[str] = None,
                               public: Optional[bool] = None, collaborative: Optional[bool] = None,
                               description: Optional[str] = None):
        """Change playlist details."""
        return self._handle_api_call(self.sp.playlist_change_details, playlist_id=playlist_id,
                                     name=name, public=public, collaborative=collaborative,
                                     description=description)
    
    def playlist_reorder_items(self, playlist_id: str, range_start: int, insert_before: int,
                              range_length: int = 1, snapshot_id: Optional[str] = None):
        """Reorder playlist items."""
        return self._handle_api_call(self.sp.playlist_reorder_items, playlist_id=playlist_id,
                                     range_start=range_start, insert_before=insert_before,
                                     range_length=range_length, snapshot_id=snapshot_id)
    
    def playlist_replace_items(self, playlist_id: str, items: List[str]):
        """Replace all playlist items."""
        return self._handle_api_call(self.sp.playlist_replace_items, playlist_id=playlist_id,
                                     items=items)
    
    def featured_playlists(self, limit: int = 20, offset: int = 0, country: Optional[str] = None,
                          locale: Optional[str] = None, timestamp: Optional[str] = None):
        """Get featured playlists."""
        kwargs = {"limit": limit, "offset": offset}
        if country:
            kwargs["country"] = country
        if locale:
            kwargs["locale"] = locale
        if timestamp:
            kwargs["timestamp"] = timestamp
        return self._handle_api_call(self.sp.featured_playlists, **kwargs)
    
    def category_playlists(self, category_id: str, limit: int = 20, offset: int = 0,
                          country: Optional[str] = None):
        """Get category's playlists."""
        kwargs = {"category_id": category_id, "limit": limit, "offset": offset}
        if country:
            kwargs["country"] = country
        return self._handle_api_call(self.sp.category_playlists, **kwargs)
    
    def playlist_cover_image(self, playlist_id: str):
        """Get playlist cover image."""
        return self._handle_api_call(self.sp.playlist_cover_image, playlist_id=playlist_id)
    
    def playlist_upload_cover_image(self, playlist_id: str, image_b64: str):
        """Upload custom playlist cover image."""
        return self._handle_api_call(self.sp.playlist_upload_cover_image, 
                                     playlist_id=playlist_id, image_b64=image_b64)
    
    def user_playlists(self, user: str, limit: int = 50, offset: int = 0):
        """Get a user's playlists."""
        return self._handle_api_call(self.sp.user_playlists, user=user, limit=limit, offset=offset)
    
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
    
    def user(self, user_id: str):
        """Get a user's profile."""
        return self._handle_api_call(self.sp.user, user=user_id)
    
    def current_user_following_artists(self, limit: int = 20, after: Optional[str] = None):
        """Get artists followed by current user."""
        kwargs = {"type": "artist", "limit": limit}
        if after:
            kwargs["after"] = after
        return self._handle_api_call(self.sp.current_user_followed_artists, **kwargs)
    
    def user_follow_artists(self, ids: List[str]):
        """Follow artists or users."""
        return self._handle_api_call(self.sp.user_follow_artists, ids=ids)
    
    def user_follow_users(self, ids: List[str]):
        """Follow users."""
        return self._handle_api_call(self.sp.user_follow_users, ids=ids)
    
    def user_unfollow_artists(self, ids: List[str]):
        """Unfollow artists or users."""
        return self._handle_api_call(self.sp.user_unfollow_artists, ids=ids)
    
    def user_unfollow_users(self, ids: List[str]):
        """Unfollow users."""
        return self._handle_api_call(self.sp.user_unfollow_users, ids=ids)
    
    def current_user_following_contains(self, ids: List[str], follow_type: str = "artist"):
        """Check if current user follows artists or users."""
        return self._handle_api_call(self.sp.current_user_following, type=follow_type, ids=ids)
    
    def playlist_is_following(self, playlist_id: str, user_ids: List[str]):
        """Check if users follow a playlist."""
        return self._handle_api_call(self.sp.playlist_is_following, playlist_id=playlist_id, user_ids=user_ids)
    
    def current_user_follow_playlist(self, playlist_id: str, public: bool = True):
        """Follow a playlist."""
        return self._handle_api_call(self.sp.current_user_follow_playlist, playlist_id=playlist_id, public=public)
    
    def current_user_unfollow_playlist(self, playlist_id: str):
        """Unfollow a playlist."""
        return self._handle_api_call(self.sp.current_user_unfollow_playlist, playlist_id=playlist_id)
    
    # Artist methods
    def artist(self, artist_id: str):
        """Get artist information."""
        return self._handle_api_call(self.sp.artist, artist_id=artist_id)
    
    def artists(self, artist_ids: List[str]):
        """Get multiple artists."""
        return self._handle_api_call(self.sp.artists, artists=artist_ids)
    
    def artist_albums(self, artist_id: str, album_type: Optional[str] = None, 
                     limit: int = 20, offset: int = 0):
        """Get artist's albums."""
        kwargs = {"artist_id": artist_id, "limit": limit, "offset": offset}
        if album_type:
            kwargs["album_type"] = album_type
        return self._handle_api_call(self.sp.artist_albums, **kwargs)
    
    def artist_top_tracks(self, artist_id: str, country: str = "US"):
        """Get artist's top tracks."""
        return self._handle_api_call(self.sp.artist_top_tracks, artist_id=artist_id, country=country)
    
    def artist_related_artists(self, artist_id: str):
        """Get related artists."""
        return self._handle_api_call(self.sp.artist_related_artists, artist_id=artist_id)
    
    # Audiobook methods
    def audiobook(self, audiobook_id: str, market: str = "US"):
        """Get audiobook information."""
        return self._handle_api_call(self.sp.get_audiobook, id=audiobook_id, market=market)
    
    def audiobooks(self, audiobook_ids: List[str], market: str = "US"):
        """Get multiple audiobooks."""
        return self._handle_api_call(self.sp.get_audiobooks, ids=audiobook_ids, market=market)
    
    def audiobook_chapters(self, audiobook_id: str, limit: int = 20, offset: int = 0, market: str = "US"):
        """Get audiobook chapters."""
        return self._handle_api_call(self.sp.get_audiobook_chapters, 
                                     id=audiobook_id, limit=limit, offset=offset, market=market)
    
    def current_user_saved_audiobooks(self, limit: int = 20, offset: int = 0):
        """Get user's saved audiobooks."""
        return self._handle_api_call(self.sp.get_users_saved_audiobooks, limit=limit, offset=offset)
    
    def current_user_saved_audiobooks_add(self, audiobook_ids: List[str]):
        """Save audiobooks to library."""
        return self._handle_api_call(self.sp.save_audiobooks, ids=audiobook_ids)
    
    def current_user_saved_audiobooks_delete(self, audiobook_ids: List[str]):
        """Remove audiobooks from library."""
        return self._handle_api_call(self.sp.remove_users_saved_audiobooks, ids=audiobook_ids)
    
    def current_user_saved_audiobooks_contains(self, audiobook_ids: List[str]):
        """Check if audiobooks are in library."""
        return self._handle_api_call(self.sp.check_users_audiobooks, ids=audiobook_ids)
    
    # Category methods
    def categories(self, country: Optional[str] = None, locale: Optional[str] = None, 
                  limit: int = 20, offset: int = 0):
        """Get browse categories."""
        kwargs = {"limit": limit, "offset": offset}
        if country:
            kwargs["country"] = country
        if locale:
            kwargs["locale"] = locale
        return self._handle_api_call(self.sp.categories, **kwargs)
    
    def category(self, category_id: str, country: Optional[str] = None, locale: Optional[str] = None):
        """Get single category."""
        kwargs = {"category_id": category_id}
        if country:
            kwargs["country"] = country
        if locale:
            kwargs["locale"] = locale
        return self._handle_api_call(self.sp.category, **kwargs)
    
    # Chapter methods
    def chapter(self, chapter_id: str, market: Optional[str] = None):
        """Get chapter information."""
        kwargs = {"id": chapter_id}
        if market:
            kwargs["market"] = market
        return self._handle_api_call(self.sp.get_chapter, **kwargs)
    
    def chapters(self, chapter_ids: List[str], market: Optional[str] = None):
        """Get multiple chapters."""
        kwargs = {"ids": chapter_ids}
        if market:
            kwargs["market"] = market
        return self._handle_api_call(self.sp.get_chapters, **kwargs)
    
    # Episode methods
    def episode(self, episode_id: str, market: Optional[str] = None):
        """Get episode information."""
        kwargs = {"id": episode_id}
        if market:
            kwargs["market"] = market
        return self._handle_api_call(self.sp.episode, **kwargs)
    
    def episodes(self, episode_ids: List[str], market: Optional[str] = None):
        """Get multiple episodes."""
        kwargs = {"ids": episode_ids}
        if market:
            kwargs["market"] = market
        return self._handle_api_call(self.sp.episodes, **kwargs)
    
    def current_user_saved_episodes(self, limit: int = 20, offset: int = 0, market: Optional[str] = None):
        """Get user's saved episodes."""
        kwargs = {"limit": limit, "offset": offset}
        if market:
            kwargs["market"] = market
        return self._handle_api_call(self.sp.current_user_saved_episodes, **kwargs)
    
    def current_user_saved_episodes_add(self, episode_ids: List[str]):
        """Save episodes to library."""
        return self._handle_api_call(self.sp.current_user_saved_episodes_add, episodes=episode_ids)
    
    def current_user_saved_episodes_delete(self, episode_ids: List[str]):
        """Remove episodes from library."""
        return self._handle_api_call(self.sp.current_user_saved_episodes_delete, episodes=episode_ids)
    
    def current_user_saved_episodes_contains(self, episode_ids: List[str]):
        """Check if episodes are in library."""
        return self._handle_api_call(self.sp.current_user_saved_episodes_contains, episodes=episode_ids)
    
    # Show methods
    def show(self, show_id: str, market: Optional[str] = None):
        """Get a show by ID."""
        kwargs = {"id": show_id}
        if market:
            kwargs["market"] = market
        return self._handle_api_call(self.sp.show, **kwargs)
    
    def shows(self, show_ids: List[str], market: Optional[str] = None):
        """Get multiple shows by IDs."""
        kwargs = {"ids": show_ids}
        if market:
            kwargs["market"] = market
        return self._handle_api_call(self.sp.shows, **kwargs)
    
    def show_episodes(self, show_id: str, limit: int = 20, offset: int = 0, market: Optional[str] = None):
        """Get episodes from a show."""
        kwargs = {"id": show_id, "limit": limit, "offset": offset}
        if market:
            kwargs["market"] = market
        return self._handle_api_call(self.sp.show_episodes, **kwargs)
    
    def current_user_saved_shows(self, limit: int = 20, offset: int = 0):
        """Get user's saved shows."""
        return self._handle_api_call(self.sp.current_user_saved_shows, limit=limit, offset=offset)
    
    def current_user_saved_shows_add(self, show_ids: List[str]):
        """Save shows to library."""
        return self._handle_api_call(self.sp.current_user_saved_shows_add, ids=show_ids)
    
    def current_user_saved_shows_delete(self, show_ids: List[str]):
        """Remove shows from library."""
        return self._handle_api_call(self.sp.current_user_saved_shows_delete, ids=show_ids)
    
    def current_user_saved_shows_contains(self, show_ids: List[str]):
        """Check if shows are in library."""
        return self._handle_api_call(self.sp.current_user_saved_shows_contains, ids=show_ids)
    
    # Track methods
    def track(self, track_id: str, market: Optional[str] = None):
        """Get a track by ID."""
        kwargs = {"id": track_id}
        if market:
            kwargs["market"] = market
        return self._handle_api_call(self.sp.track, **kwargs)
    
    def tracks(self, track_ids: List[str], market: Optional[str] = None):
        """Get multiple tracks by IDs."""
        kwargs = {"ids": track_ids}
        if market:
            kwargs["market"] = market
        return self._handle_api_call(self.sp.tracks, **kwargs)
    
    def audio_features(self, track_ids: List[str]):
        """Get audio features for multiple tracks."""
        return self._handle_api_call(self.sp.audio_features, tracks=track_ids)
    
    def audio_analysis(self, track_id: str):
        """Get audio analysis for a track."""
        return self._handle_api_call(self.sp.audio_analysis, track_id)
    
    # Genre methods
    def recommendation_genre_seeds(self):
        """Get available genre seeds for recommendations."""
        return self._handle_api_call(self.sp.recommendation_genre_seeds)
    
    # Market methods
    def available_markets(self):
        """Get available markets."""
        return self._handle_api_call(self.sp.available_markets)
