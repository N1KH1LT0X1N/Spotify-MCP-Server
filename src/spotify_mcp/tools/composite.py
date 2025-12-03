"""
Composite tools that combine multiple Spotify operations for convenience.

These tools perform multi-step operations that users commonly want to do together.
Each composite tool reduces the number of individual API calls needed.
"""

from typing import Optional, List, Dict, Any
from spotify_mcp.spotify_client import SpotifyClient


def create_playlist_with_tracks(sp: SpotifyClient, user_id: str, name: str, 
                                tracks: List[str], public: bool = True,
                                description: str = "") -> Dict[str, Any]:
    """
    Create a playlist and add tracks in one operation.
    
    Args:
        sp: SpotifyClient instance
        user_id: User ID who owns the playlist
        name: Playlist name
        tracks: List of track URIs to add
        public: Whether playlist is public
        description: Playlist description
        
    Returns:
        Created playlist info with added tracks
    """
    try:
        # Create the playlist
        playlist = sp.user_playlist_create(
            user=user_id,
            name=name,
            public=public,
            description=description
        )
        
        playlist_id = playlist['id']
        
        # Add tracks in batches (Spotify API limit is 100 per request)
        if tracks:
            for i in range(0, len(tracks), 100):
                batch = tracks[i:i+100]
                sp.playlist_add_items(playlist_id, batch)
        
        return {
            "playlist": playlist,
            "tracks_added": len(tracks),
            "status": "success"
        }
    except Exception as e:
        raise Exception(f"Failed to create playlist with tracks: {str(e)}")


def get_artist_full_profile(sp: SpotifyClient, artist_id: str) -> Dict[str, Any]:
    """
    Get comprehensive artist information including top tracks and albums.
    
    Args:
        sp: SpotifyClient instance
        artist_id: Artist ID
        
    Returns:
        Complete artist profile with discography and top tracks
    """
    try:
        artist = sp.artist(artist_id)
        top_tracks = sp.artist_top_tracks(artist_id)
        albums = sp.artist_albums(artist_id, limit=20)
        
        return {
            "artist": artist,
            "top_tracks": top_tracks.get('tracks', [])[:10],
            "albums": albums.get('items', []),
            "total_albums": albums.get('total', 0)
        }
    except Exception as e:
        raise Exception(f"Failed to get artist profile: {str(e)}")


def search_and_create_playlist(sp: SpotifyClient, query: str, user_id: str,
                               playlist_name: str, limit: int = 20,
                               search_type: str = "track") -> Dict[str, Any]:
    """
    Search for tracks/albums/artists and create a playlist from results.
    
    Args:
        sp: SpotifyClient instance
        query: Search query
        user_id: User ID for playlist
        playlist_name: Name for the new playlist
        limit: Number of results to get
        search_type: Type to search for (track, album, artist)
        
    Returns:
        Created playlist with search results
    """
    try:
        # Search for content
        results = sp.search(q=query, limit=limit, type=search_type)
        
        # Extract URIs based on search type
        uris = []
        if search_type == "track" and "tracks" in results:
            uris = [track['uri'] for track in results['tracks']['items']]
        elif search_type == "album" and "albums" in results:
            # Get first track from each album
            for album in results['albums']['items'][:limit]:
                album_tracks = sp.album_tracks(album['id'], limit=1)
                if album_tracks['items']:
                    uris.append(album_tracks['items'][0]['uri'])
        elif search_type == "artist" and "artists" in results:
            # Get top tracks from each artist
            for artist in results['artists']['items'][:limit]:
                artist_tracks = sp.artist_top_tracks(artist['id'])
                if artist_tracks['tracks']:
                    uris.append(artist_tracks['tracks'][0]['uri'])
        
        if not uris:
            raise Exception(f"No {search_type}s found for '{query}'")
        
        # Create playlist with found tracks
        playlist = create_playlist_with_tracks(
            sp, user_id, playlist_name, uris,
            description=f"Created from search: {query}"
        )
        
        return playlist
    except Exception as e:
        raise Exception(f"Failed to search and create playlist: {str(e)}")


def get_listening_summary(sp: SpotifyClient, time_range: str = "medium_term") -> Dict[str, Any]:
    """
    Get a comprehensive summary of user's listening habits.
    
    Args:
        sp: SpotifyClient instance
        time_range: Time range for analysis (short_term, medium_term, long_term)
        
    Returns:
        Listening summary with top tracks, artists, and user info
    """
    try:
        user_profile = sp.current_user()
        top_tracks = sp.current_user_top_tracks(limit=10, time_range=time_range)
        top_artists = sp.current_user_top_artists(limit=10, time_range=time_range)
        recently_played = sp.current_user_recently_played(limit=10)
        
        return {
            "user": {
                "name": user_profile.get('display_name', 'Unknown'),
                "followers": user_profile.get('followers', {}).get('total', 0),
                "country": user_profile.get('country', 'Unknown')
            },
            "top_tracks": top_tracks.get('items', [])[:5],
            "top_artists": top_artists.get('items', [])[:5],
            "recently_played": recently_played.get('items', [])[:5],
            "time_range": time_range
        }
    except Exception as e:
        raise Exception(f"Failed to get listening summary: {str(e)}")


def save_multiple_items(sp: SpotifyClient, track_ids: Optional[List[str]] = None,
                       album_ids: Optional[List[str]] = None,
                       artist_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Save multiple types of items to user's library in one operation.
    
    Args:
        sp: SpotifyClient instance
        track_ids: Track IDs to save
        album_ids: Album IDs to save
        artist_ids: Artist IDs to follow
        
    Returns:
        Summary of items saved
    """
    try:
        results = {"tracks_saved": 0, "albums_saved": 0, "artists_followed": 0}
        
        if track_ids:
            sp.current_user_saved_tracks_add(track_ids)
            results["tracks_saved"] = len(track_ids)
        
        if album_ids:
            sp.current_user_saved_albums_add(album_ids)
            results["albums_saved"] = len(album_ids)
        
        if artist_ids:
            sp.user_follow_artists(artist_ids)
            results["artists_followed"] = len(artist_ids)
        
        return results
    except Exception as e:
        raise Exception(f"Failed to save items: {str(e)}")


def compare_user_libraries(sp: SpotifyClient, user_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    Compare current user's library with another user's public profile.
    
    Args:
        sp: SpotifyClient instance
        user_id: User ID to compare with
        limit: Number of playlists to check
        
    Returns:
        Comparison of listening preferences
    """
    try:
        current_user = sp.current_user()
        other_user = sp.user(user_id)
        current_playlists = sp.current_user_playlists(limit=limit)
        other_playlists = sp.user_playlists(user_id, limit=limit)
        
        return {
            "current_user": {
                "name": current_user.get('display_name'),
                "playlists_count": current_playlists.get('total', 0)
            },
            "other_user": {
                "name": other_user.get('display_name'),
                "playlists_count": other_playlists.get('total', 0),
                "followers": other_user.get('followers', {}).get('total', 0)
            },
            "current_user_playlists": [p['name'] for p in current_playlists['items'][:10]],
            "other_user_playlists": [p['name'] for p in other_playlists['items'][:10]]
        }
    except Exception as e:
        raise Exception(f"Failed to compare libraries: {str(e)}")


COMPOSITE_TOOLS = {
    "create_playlist_with_tracks": create_playlist_with_tracks,
    "get_artist_full_profile": get_artist_full_profile,
    "search_and_create_playlist": search_and_create_playlist,
    "get_listening_summary": get_listening_summary,
    "save_multiple_items": save_multiple_items,
    "compare_user_libraries": compare_user_libraries,
}
