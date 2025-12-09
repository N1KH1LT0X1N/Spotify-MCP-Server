"""
Pydantic models for structured output in Spotify MCP Server.

These models define the shape of data returned by tools, ensuring
type safety, validation, and better documentation for Claude.
"""

from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================================================
# Base Models
# ============================================================================

class Artist(BaseModel):
    """Spotify artist information."""
    id: Optional[str] = None
    name: str
    uri: Optional[str] = None
    genres: Optional[List[str]] = None
    popularity: Optional[int] = None
    followers: Optional[int] = None


class Album(BaseModel):
    """Spotify album information."""
    id: Optional[str] = None
    name: str
    uri: Optional[str] = None
    artists: Optional[List[Artist]] = None
    release_date: Optional[str] = None
    total_tracks: Optional[int] = None
    album_type: Optional[str] = None


class TrackBase(BaseModel):
    """Base track information."""
    id: Optional[str] = None
    name: str
    uri: Optional[str] = None
    duration_ms: Optional[int] = None
    explicit: Optional[bool] = False
    popularity: Optional[int] = None


class Track(TrackBase):
    """Full track information with artists and album."""
    artists: List[Artist] = Field(default_factory=list)
    album: Optional[Album] = None


class Device(BaseModel):
    """Spotify playback device."""
    id: Optional[str] = None
    name: str
    type: str
    is_active: bool = False
    is_private_session: bool = False
    is_restricted: bool = False
    volume_percent: Optional[int] = None


class PlaybackContext(BaseModel):
    """Playback context (album, playlist, artist)."""
    type: Optional[str] = None
    uri: Optional[str] = None


# ============================================================================
# Playback Models
# ============================================================================

class PlaybackState(BaseModel):
    """Current playback state."""
    is_playing: bool = False
    shuffle_state: bool = False
    repeat_state: str = "off"
    progress_ms: int = 0
    track: Optional[Track] = None
    device: Optional[Device] = None
    context: Optional[PlaybackContext] = None
    message: Optional[str] = None  # For "No active playback" messages


class PlaybackAction(BaseModel):
    """Result of a playback action."""
    success: bool
    message: str
    device_id: Optional[str] = None


class VolumeAction(PlaybackAction):
    """Result of a volume change action."""
    volume_percent: Optional[int] = None


class ShuffleAction(PlaybackAction):
    """Result of a shuffle toggle action."""
    shuffle_state: Optional[bool] = None


class RepeatAction(PlaybackAction):
    """Result of a repeat mode change action."""
    repeat_state: Optional[str] = None


class SeekAction(PlaybackAction):
    """Result of a seek action."""
    position_ms: Optional[int] = None


class DeviceList(BaseModel):
    """List of available playback devices."""
    devices: List[Device]
    total_devices: int


class TransferAction(PlaybackAction):
    """Result of a playback transfer action."""
    force_play: Optional[bool] = None


# ============================================================================
# Search Models
# ============================================================================

class SearchResult(BaseModel):
    """Search result from Spotify."""
    query: str
    type: str
    items: List[Any]  # Can be Track, Album, Artist, or Playlist
    total: int
    limit: int
    offset: int
    has_more: bool


# ============================================================================
# Library Models
# ============================================================================

class SavedTrack(BaseModel):
    """Track saved in user's library."""
    added_at: Optional[str] = None
    track: Track


class SavedTrackList(BaseModel):
    """List of saved tracks."""
    tracks: List[SavedTrack]
    total: int
    limit: int
    offset: int
    has_more: bool


class LibraryAction(BaseModel):
    """Result of a library action (save/remove)."""
    success: bool
    message: str
    track_count: int
    track_ids: List[str]


class SavedTrackCheck(BaseModel):
    """Result of checking if tracks are saved."""
    track_id: str
    is_saved: bool


class SavedTrackCheckResult(BaseModel):
    """Result of checking multiple tracks."""
    tracks: List[SavedTrackCheck]
    total_checked: int
    total_saved: int


# ============================================================================
# Playlist Models
# ============================================================================

class PlaylistOwner(BaseModel):
    """Playlist owner information."""
    id: Optional[str] = None
    display_name: Optional[str] = None


class PlaylistBase(BaseModel):
    """Basic playlist information."""
    id: str
    name: str
    uri: str
    description: Optional[str] = None
    owner: Optional[PlaylistOwner] = None
    total_tracks: int = 0
    public: bool = False
    collaborative: bool = False
    snapshot_id: Optional[str] = None


class Playlist(PlaylistBase):
    """Full playlist with optional tracks."""
    followers: Optional[int] = None
    tracks: Optional[Any] = None  # TrackList when included


class PlaylistList(BaseModel):
    """List of playlists."""
    playlists: List[PlaylistBase]
    total: int
    limit: int
    offset: int
    has_more: bool


class PlaylistCreated(BaseModel):
    """Result of playlist creation."""
    success: bool
    message: str
    playlist: PlaylistBase


class PlaylistAction(BaseModel):
    """Result of a playlist action."""
    success: bool
    message: str
    track_count: Optional[int] = None
    snapshot_id: Optional[str] = None


class PlaylistDetailsUpdate(BaseModel):
    """Result of updating playlist details."""
    success: bool
    message: str
    updated_fields: dict


class PlaylistCoverImage(BaseModel):
    """Playlist cover image."""
    url: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None


class PlaylistCover(BaseModel):
    """Playlist cover image result."""
    playlist_id: str
    images: List[PlaylistCoverImage]


# ============================================================================
# Queue Models
# ============================================================================

class Queue(BaseModel):
    """Current playback queue."""
    currently_playing: Optional[Track] = None
    queue_length: int = 0
    next_tracks: List[Track] = Field(default_factory=list)


class QueueAction(BaseModel):
    """Result of queue action."""
    success: bool
    message: str
    uri: Optional[str] = None


# ============================================================================
# User Models
# ============================================================================

class UserProfile(BaseModel):
    """Spotify user profile."""
    id: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    country: Optional[str] = None
    product: Optional[str] = None
    followers: int = 0
    uri: Optional[str] = None


class TopItemsList(BaseModel):
    """User's top tracks or artists."""
    items: List[Any]  # Track or Artist
    total: int
    limit: int
    offset: int
    time_range: str


class FollowedArtists(BaseModel):
    """List of followed artists."""
    artists: List[Artist]
    total: int
    cursor_after: Optional[str] = None


class FollowAction(BaseModel):
    """Result of follow/unfollow action."""
    success: bool
    message: str
    ids: List[str]


class FollowCheck(BaseModel):
    """Result of follow check."""
    id: str
    is_following: bool


class FollowCheckResult(BaseModel):
    """Result of checking multiple follows."""
    items: List[FollowCheck]
    type: str


# ============================================================================
# Album Models
# ============================================================================

class AlbumFull(BaseModel):
    """Full album information."""
    id: str
    name: str
    uri: str
    artists: List[Artist]
    release_date: Optional[str] = None
    total_tracks: int = 0
    album_type: Optional[str] = None
    genres: Optional[List[str]] = None
    popularity: Optional[int] = None
    label: Optional[str] = None


class AlbumTrackList(BaseModel):
    """List of album tracks."""
    album_id: str
    tracks: List[TrackBase]
    total: int
    limit: int
    offset: int
    has_more: bool


class SavedAlbum(BaseModel):
    """Album saved in user's library."""
    added_at: Optional[str] = None
    album: AlbumFull


class SavedAlbumList(BaseModel):
    """List of saved albums."""
    albums: List[SavedAlbum]
    total: int
    limit: int
    offset: int
    has_more: bool


class AlbumAction(BaseModel):
    """Result of album library action."""
    success: bool
    message: str
    album_count: int
    album_ids: List[str]


class NewReleases(BaseModel):
    """New album releases."""
    albums: List[AlbumFull]
    total: int
    limit: int
    offset: int


# ============================================================================
# Artist Models
# ============================================================================

class ArtistFull(BaseModel):
    """Full artist information."""
    id: str
    name: str
    uri: str
    genres: List[str] = Field(default_factory=list)
    popularity: int = 0
    followers: int = 0
    images: Optional[List[dict]] = None


class ArtistTopTracks(BaseModel):
    """Artist's top tracks."""
    artist_id: str
    country: str
    tracks: List[Track]


class ArtistAlbums(BaseModel):
    """Artist's albums."""
    artist_id: str
    albums: List[AlbumFull]
    total: int
    limit: int
    offset: int
    has_more: bool


# ============================================================================
# Episode/Show Models
# ============================================================================

class Episode(BaseModel):
    """Podcast episode."""
    id: str
    name: str
    uri: str
    description: Optional[str] = None
    duration_ms: Optional[int] = None
    release_date: Optional[str] = None
    show: Optional[dict] = None


class Show(BaseModel):
    """Podcast show."""
    id: str
    name: str
    uri: str
    description: Optional[str] = None
    publisher: Optional[str] = None
    total_episodes: int = 0


class SavedEpisode(BaseModel):
    """Episode saved in user's library."""
    added_at: Optional[str] = None
    episode: Episode


class SavedShow(BaseModel):
    """Show saved in user's library."""
    added_at: Optional[str] = None
    show: Show


# ============================================================================
# Category Models
# ============================================================================

class Category(BaseModel):
    """Browse category."""
    id: str
    name: str
    icons: Optional[List[dict]] = None


# ============================================================================
# Market Models
# ============================================================================

class Markets(BaseModel):
    """Available Spotify markets."""
    markets: List[str]


# ============================================================================
# Recently Played Models
# ============================================================================

class PlayHistoryItem(BaseModel):
    """Recently played track item."""
    track: Track
    played_at: Optional[str] = None
    context: Optional[PlaybackContext] = None


class RecentlyPlayed(BaseModel):
    """Recently played tracks."""
    items: List[PlayHistoryItem]
    total: int
    cursors: Optional[dict] = None


# ============================================================================
# Composite Tool Models
# ============================================================================

class PlaylistWithTracks(BaseModel):
    """Result of creating a playlist with tracks."""
    playlist: PlaylistBase
    tracks_added: int
    status: str


class ArtistFullProfile(BaseModel):
    """Complete artist profile."""
    artist: ArtistFull
    top_tracks: List[Track]
    albums: List[AlbumFull]
    total_albums: int


class ListeningSummary(BaseModel):
    """User's listening summary."""
    user: dict
    top_tracks: List[Track]
    top_artists: List[Artist]
    recently_played: List[PlayHistoryItem]
    time_range: str


class MultiSaveResult(BaseModel):
    """Result of saving multiple items."""
    tracks_saved: int = 0
    albums_saved: int = 0
    artists_followed: int = 0


class LibraryComparison(BaseModel):
    """Comparison of user libraries."""
    current_user: dict
    other_user: dict
    current_user_playlists: List[str]
    other_user_playlists: List[str]
