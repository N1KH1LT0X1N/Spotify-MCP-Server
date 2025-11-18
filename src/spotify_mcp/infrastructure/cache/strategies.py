"""Cache strategies and key generation for Spotify data types."""

import hashlib
from enum import Enum
from typing import Optional


class CacheStrategy(Enum):
    """
    Caching strategies by data type.

    TTL (time-to-live) is optimized based on how frequently data changes:
    - Static data (track metadata): Long TTL (24h)
    - Semi-static (playlists): Medium TTL (5min)
    - Dynamic (playback state): Short TTL (10s)
    """

    # Static data (rarely changes)
    TRACK_METADATA = (3600 * 24, "track:")  # 24 hours
    ALBUM_METADATA = (3600 * 24, "album:")  # 24 hours
    ARTIST_METADATA = (3600 * 24, "artist:")  # 24 hours
    AUDIO_FEATURES = (3600 * 24 * 7, "audio_features:")  # 1 week
    AUDIOBOOK_METADATA = (3600 * 24, "audiobook:")  # 24 hours
    SHOW_METADATA = (3600 * 24, "show:")  # 24 hours
    EPISODE_METADATA = (3600 * 24, "episode:")  # 24 hours

    # Semi-static data (changes occasionally)
    PLAYLIST_METADATA = (300, "playlist:")  # 5 minutes
    USER_LIBRARY = (180, "library:")  # 3 minutes
    SEARCH_RESULTS = (600, "search:")  # 10 minutes
    RECOMMENDATIONS = (600, "recommendations:")  # 10 minutes
    CATEGORIES = (3600, "categories:")  # 1 hour
    GENRES = (3600 * 24, "genres:")  # 24 hours
    MARKETS = (3600 * 24, "markets:")  # 24 hours

    # Dynamic data (changes frequently)
    PLAYBACK_STATE = (10, "playback:")  # 10 seconds
    QUEUE = (30, "queue:")  # 30 seconds
    DEVICES = (60, "devices:")  # 1 minute
    RECENTLY_PLAYED = (60, "recent:")  # 1 minute

    # User data
    USER_PROFILE = (3600, "user:")  # 1 hour
    USER_TOP_ITEMS = (3600 * 6, "top:")  # 6 hours
    FOLLOWED_ARTISTS = (3600, "following:")  # 1 hour

    def __init__(self, ttl: int, prefix: str):
        self.ttl = ttl
        self.prefix = prefix


class CacheKeyGenerator:
    """Generate consistent cache keys for Spotify resources."""

    @staticmethod
    def track(track_id: str) -> str:
        """Generate cache key for track."""
        return f"{CacheStrategy.TRACK_METADATA.prefix}{track_id}"

    @staticmethod
    def album(album_id: str) -> str:
        """Generate cache key for album."""
        return f"{CacheStrategy.ALBUM_METADATA.prefix}{album_id}"

    @staticmethod
    def artist(artist_id: str) -> str:
        """Generate cache key for artist."""
        return f"{CacheStrategy.ARTIST_METADATA.prefix}{artist_id}"

    @staticmethod
    def playlist(playlist_id: str) -> str:
        """Generate cache key for playlist."""
        return f"{CacheStrategy.PLAYLIST_METADATA.prefix}{playlist_id}"

    @staticmethod
    def audio_features(track_id: str) -> str:
        """Generate cache key for audio features."""
        return f"{CacheStrategy.AUDIO_FEATURES.prefix}{track_id}"

    @staticmethod
    def audiobook(audiobook_id: str) -> str:
        """Generate cache key for audiobook."""
        return f"{CacheStrategy.AUDIOBOOK_METADATA.prefix}{audiobook_id}"

    @staticmethod
    def show(show_id: str) -> str:
        """Generate cache key for show."""
        return f"{CacheStrategy.SHOW_METADATA.prefix}{show_id}"

    @staticmethod
    def episode(episode_id: str) -> str:
        """Generate cache key for episode."""
        return f"{CacheStrategy.EPISODE_METADATA.prefix}{episode_id}"

    @staticmethod
    def search(query: str, search_type: str, limit: int, offset: int = 0) -> str:
        """Generate cache key for search results."""
        key_data = f"{query}:{search_type}:{limit}:{offset}"
        hash_key = hashlib.md5(key_data.encode()).hexdigest()
        return f"{CacheStrategy.SEARCH_RESULTS.prefix}{hash_key}"

    @staticmethod
    def recommendations(
        seed_artists: Optional[list] = None,
        seed_tracks: Optional[list] = None,
        seed_genres: Optional[list] = None,
        limit: int = 20,
    ) -> str:
        """Generate cache key for recommendations."""
        seeds = f"{seed_artists or ''}:{seed_tracks or ''}:{seed_genres or ''}:{limit}"
        hash_key = hashlib.md5(seeds.encode()).hexdigest()
        return f"{CacheStrategy.RECOMMENDATIONS.prefix}{hash_key}"

    @staticmethod
    def playback_state(user_id: Optional[str] = None) -> str:
        """Generate cache key for playback state."""
        suffix = f":{user_id}" if user_id else ""
        return f"{CacheStrategy.PLAYBACK_STATE.prefix}state{suffix}"

    @staticmethod
    def queue(user_id: Optional[str] = None) -> str:
        """Generate cache key for queue."""
        suffix = f":{user_id}" if user_id else ""
        return f"{CacheStrategy.QUEUE.prefix}current{suffix}"

    @staticmethod
    def devices(user_id: Optional[str] = None) -> str:
        """Generate cache key for devices."""
        suffix = f":{user_id}" if user_id else ""
        return f"{CacheStrategy.DEVICES.prefix}list{suffix}"

    @staticmethod
    def user_profile(user_id: str) -> str:
        """Generate cache key for user profile."""
        return f"{CacheStrategy.USER_PROFILE.prefix}{user_id}"

    @staticmethod
    def user_library(user_id: str, library_type: str) -> str:
        """Generate cache key for user library."""
        return f"{CacheStrategy.USER_LIBRARY.prefix}{user_id}:{library_type}"

    @staticmethod
    def followed_artists(user_id: str) -> str:
        """Generate cache key for followed artists."""
        return f"{CacheStrategy.FOLLOWED_ARTISTS.prefix}{user_id}"
