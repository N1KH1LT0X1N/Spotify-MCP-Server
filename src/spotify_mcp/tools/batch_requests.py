"""
Request batching utilities for Spotify API optimization.

Combines multiple related requests into single batch operations to reduce
API calls and improve performance.
"""

from typing import List, Dict, Any, Optional
from spotify_mcp.spotify_client import SpotifyClient


class BatchRequestHandler:
    """Handles batching of multiple API requests for better performance."""
    
    @staticmethod
    def get_multiple_tracks_with_details(sp: SpotifyClient, track_ids: List[str],
                                         include_albums: bool = False) -> List[Dict[str, Any]]:
        """
        Efficiently get track details (up to 50 at a time).
        
        Args:
            sp: SpotifyClient instance
            track_ids: List of track IDs
            include_albums: Also fetch album details
            
        Returns:
            List of track data with optional album info
        """
        results = []
        
        # Batch requests in groups of 50 (Spotify API limit)
        for i in range(0, len(track_ids), 50):
            batch = track_ids[i:i+50]
            tracks = sp.tracks(batch)
            
            for track in tracks.get('items', []):
                track_data = {
                    "id": track.get('id'),
                    "name": track.get('name'),
                    "artist": track['artists'][0]['name'] if track.get('artists') else 'Unknown',
                    "duration_ms": track.get('duration_ms'),
                    "popularity": track.get('popularity'),
                }
                
                if include_albums and track.get('album'):
                    album = track['album']
                    track_data['album'] = {
                        "name": album.get('name'),
                        "release_date": album.get('release_date'),
                        "images": album.get('images', [])
                    }
                
                results.append(track_data)
        
        return results
    
    @staticmethod
    def get_multiple_artists_with_details(sp: SpotifyClient, artist_ids: List[str],
                                         include_top_tracks: bool = False) -> List[Dict[str, Any]]:
        """
        Efficiently get artist details (up to 50 at a time).
        
        Args:
            sp: SpotifyClient instance
            artist_ids: List of artist IDs
            include_top_tracks: Also fetch top tracks for each artist
            
        Returns:
            List of artist data with optional top tracks
        """
        results = []
        
        # Batch requests in groups of 50 (Spotify API limit)
        for i in range(0, len(artist_ids), 50):
            batch = artist_ids[i:i+50]
            artists = sp.artists(batch)
            
            for artist in artists.get('artists', []):
                artist_data = {
                    "id": artist.get('id'),
                    "name": artist.get('name'),
                    "genres": artist.get('genres', []),
                    "popularity": artist.get('popularity'),
                    "followers": artist.get('followers', {}).get('total', 0),
                    "images": artist.get('images', [])
                }
                
                if include_top_tracks:
                    top_tracks = sp.artist_top_tracks(artist['id'])
                    artist_data['top_tracks'] = [
                        {
                            "name": t.get('name'),
                            "popularity": t.get('popularity')
                        }
                        for t in top_tracks.get('tracks', [])[:3]
                    ]
                
                results.append(artist_data)
        
        return results
    
    @staticmethod
    def get_multiple_albums_with_tracks(sp: SpotifyClient, album_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Efficiently get album details with tracklists.
        
        Args:
            sp: SpotifyClient instance
            album_ids: List of album IDs
            
        Returns:
            List of album data with tracks
        """
        results = []
        
        # Batch requests in groups of 20
        for i in range(0, len(album_ids), 20):
            batch = album_ids[i:i+20]
            albums = sp.albums(batch)
            
            for album in albums.get('albums', []):
                album_data = {
                    "id": album.get('id'),
                    "name": album.get('name'),
                    "artist": album['artists'][0]['name'] if album.get('artists') else 'Unknown',
                    "release_date": album.get('release_date'),
                    "total_tracks": album.get('total_tracks'),
                    "images": album.get('images', []),
                    "tracks": []
                }
                
                # Get track list
                tracks = sp.album_tracks(album['id'], limit=50)
                album_data['tracks'] = [
                    {
                        "name": t.get('name'),
                        "artist": t['artists'][0]['name'] if t.get('artists') else 'Unknown',
                        "duration_ms": t.get('duration_ms')
                    }
                    for t in tracks.get('items', [])
                ]
                
                results.append(album_data)
        
        return results
    
    @staticmethod
    def bulk_check_saved_items(sp: SpotifyClient, 
                               track_ids: Optional[List[str]] = None,
                               album_ids: Optional[List[str]] = None,
                               artist_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Check if multiple items are saved in user's library (up to 50 per call).
        
        Args:
            sp: SpotifyClient instance
            track_ids: Track IDs to check
            album_ids: Album IDs to check
            artist_ids: Artist IDs to check (for follow status)
            
        Returns:
            Dictionary with saved status for each item
        """
        results = {
            "tracks": {},
            "albums": {},
            "artists": {}
        }
        
        # Check saved tracks
        if track_ids:
            for i in range(0, len(track_ids), 50):
                batch = track_ids[i:i+50]
                statuses = sp.current_user_saved_tracks_contains(batch)
                for track_id, is_saved in zip(batch, statuses):
                    results["tracks"][track_id] = is_saved
        
        # Check saved albums
        if album_ids:
            for i in range(0, len(album_ids), 50):
                batch = album_ids[i:i+50]
                statuses = sp.current_user_saved_albums_contains(batch)
                for album_id, is_saved in zip(batch, statuses):
                    results["albums"][album_id] = is_saved
        
        # Check followed artists
        if artist_ids:
            for i in range(0, len(artist_ids), 50):
                batch = artist_ids[i:i+50]
                statuses = sp.current_user_following_contains(batch, follow_type="artist")
                for artist_id, is_followed in zip(batch, statuses):
                    results["artists"][artist_id] = is_followed
        
        return results
    
    @staticmethod
    def bulk_save_items(sp: SpotifyClient,
                       track_ids: Optional[List[str]] = None,
                       album_ids: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Efficiently save multiple items (tracks/albums) in batches.
        
        Args:
            sp: SpotifyClient instance
            track_ids: Track IDs to save
            album_ids: Album IDs to save
            
        Returns:
            Count of saved items
        """
        saved_count = {"tracks": 0, "albums": 0}
        
        # Save tracks in batches of 50
        if track_ids:
            for i in range(0, len(track_ids), 50):
                batch = track_ids[i:i+50]
                sp.current_user_saved_tracks_add(batch)
                saved_count["tracks"] += len(batch)
        
        # Save albums in batches of 50
        if album_ids:
            for i in range(0, len(album_ids), 50):
                batch = album_ids[i:i+50]
                sp.current_user_saved_albums_add(batch)
                saved_count["albums"] += len(batch)
        
        return saved_count


class CacheOptimizer:
    """Optimizes cache usage for common patterns."""
    
    @staticmethod
    def warm_user_cache(sp: SpotifyClient) -> Dict[str, int]:
        """
        Pre-populate cache with commonly accessed user data.
        
        Args:
            sp: SpotifyClient instance
            
        Returns:
            Count of items cached
        """
        cached_items = {
            "user_profile": 0,
            "top_tracks": 0,
            "top_artists": 0,
            "saved_tracks": 0,
            "playlists": 0
        }
        
        try:
            # Cache current user profile
            sp.current_user()
            cached_items["user_profile"] = 1
            
            # Cache top tracks and artists
            sp.current_user_top_tracks(limit=50, time_range="medium_term")
            cached_items["top_tracks"] = 50
            
            sp.current_user_top_artists(limit=50, time_range="medium_term")
            cached_items["top_artists"] = 50
            
            # Cache saved tracks
            sp.current_user_saved_tracks(limit=50)
            cached_items["saved_tracks"] = 50
            
            # Cache playlists
            sp.current_user_playlists(limit=50)
            cached_items["playlists"] = 50
            
        except Exception as e:
            # Log but don't fail if warming fails
            import logging
            logging.warning(f"Cache warming partially failed: {e}")
        
        return cached_items
    
    @staticmethod
    def get_cache_stats(sp: SpotifyClient) -> Dict[str, Any]:
        """
        Get statistics about cache usage.
        
        Args:
            sp: SpotifyClient instance
            
        Returns:
            Cache statistics
        """
        from .infrastructure.cache import get_cache_manager
        
        manager = get_cache_manager()
        
        return {
            "cache_backend": manager.__class__.__name__,
            "cache_enabled": manager is not None,
            "estimated_items_cached": manager.get_size() if hasattr(manager, 'get_size') else 'unknown'
        }
