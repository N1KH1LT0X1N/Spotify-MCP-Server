"""Compatibility shim exposing the enhanced FastMCP server as `spotify_mcp.server`.
Keeps legacy `TOOL_FUNCTIONS` mapping for tests while delegating to tool modules."""

from typing import Callable, Dict

from spotify_mcp import spotify_server as _enhanced

# Import tool functions directly from their modules
from spotify_mcp.tools import (
    playback, search, library, albums, playlists, queue, user,
    artists, episodes, markets, shows, tracks, composite, categories
)

# Build TOOL_FUNCTIONS from actual implementations (80 + 6 composite = 86 total)
TOOL_FUNCTIONS: Dict[str, Callable] = {
    # Playback (12 tools)
    "play": playback.play,
    "pause": playback.pause,
    "skip_next": playback.skip_next,
    "skip_previous": playback.skip_previous,
    "get_current_playback": playback.get_current_playback,
    "get_available_devices": playback.get_available_devices,
    "transfer_playback": playback.transfer_playback,
    "set_volume": playback.set_volume,
    "set_shuffle": playback.set_shuffle,
    "set_repeat": playback.set_repeat,
    "seek_to_position": playback.seek_to_position,
    "get_recently_played": playback.get_recently_played,
    
    # Search (1 tool)
    "search": search.search,
    
    # Library (4 tools)
    "get_saved_tracks": library.get_saved_tracks,
    "save_tracks": library.save_tracks,
    "remove_saved_tracks": library.remove_saved_tracks,
    "check_saved_tracks": library.check_saved_tracks,
    
    # Albums (8 tools)
    "get_album": albums.get_album,
    "get_several_albums": albums.get_several_albums,
    "get_album_tracks": albums.get_album_tracks,
    "get_saved_albums": albums.get_saved_albums,
    "save_albums": albums.save_albums,
    "remove_saved_albums": albums.remove_saved_albums,
    "check_saved_albums": albums.check_saved_albums,
    "get_new_releases": albums.get_new_releases,
    
    # Playlists (12 tools)
    "get_user_playlists": playlists.get_user_playlists,
    "get_playlist": playlists.get_playlist,
    "create_playlist": playlists.create_playlist,
    "add_tracks_to_playlist": playlists.add_tracks_to_playlist,
    "remove_tracks_from_playlist": playlists.remove_tracks_from_playlist,
    "change_playlist_details": playlists.change_playlist_details,
    "update_playlist_items": playlists.update_playlist_items,
    "get_playlist_cover_image": playlists.get_playlist_cover_image,
    "add_custom_playlist_cover_image": playlists.add_custom_playlist_cover_image,
    "get_user_playlists_by_id": playlists.get_user_playlists_by_id,
    "follow_playlist": playlists.follow_playlist,
    "unfollow_playlist": playlists.unfollow_playlist,
    
    # Queue (2 tools)
    "get_queue": queue.get_queue,
    "add_to_queue": queue.add_to_queue,
    
    # User (8 tools)
    "get_current_user": user.get_current_user,
    "get_top_items": user.get_top_items,
    "get_user_profile": user.get_user_profile,
    "get_followed_artists": user.get_followed_artists,
    "follow_artists_or_users": user.follow_artists_or_users,
    "unfollow_artists_or_users": user.unfollow_artists_or_users,
    "check_following_artists_or_users": user.check_following_artists_or_users,
    "check_current_user_follows_playlist": user.check_current_user_follows_playlist,
    
    # Artists (4 tools)
    "get_artist": artists.get_artist,
    "get_several_artists": artists.get_several_artists,
    "get_artist_albums": artists.get_artist_albums,
    "get_artist_top_tracks": artists.get_artist_top_tracks,
    
    # Categories (2 tools)
    "get_several_browse_categories": categories.get_several_browse_categories,
    "get_single_browse_category": categories.get_single_browse_category,
    
    # Episodes (6 tools)
    "get_episode": episodes.get_episode,
    "get_several_episodes": episodes.get_several_episodes,
    "get_saved_episodes": episodes.get_saved_episodes,
    "save_episodes": episodes.save_episodes,
    "remove_saved_episodes": episodes.remove_saved_episodes,
    "check_saved_episodes": episodes.check_saved_episodes,
    
    # Markets (1 tool)
    "get_available_markets": markets.get_available_markets,
    
    # Shows (7 tools)
    "get_show": shows.get_show,
    "get_several_shows": shows.get_several_shows,
    "get_show_episodes": shows.get_show_episodes,
    "get_saved_shows": shows.get_saved_shows,
    "save_shows": shows.save_shows,
    "remove_saved_shows": shows.remove_saved_shows,
    "check_saved_shows": shows.check_saved_shows,
    
    # Tracks (2 tools)
    "get_track": tracks.get_track,
    "get_several_tracks": tracks.get_several_tracks,
    
    # Composite (6 tools)
    "create_playlist_with_tracks": composite.create_playlist_with_tracks,
    "get_artist_full_profile": composite.get_artist_full_profile,
    "search_and_create_playlist": composite.search_and_create_playlist,
    "get_listening_summary": composite.get_listening_summary,
    "save_multiple_items": composite.save_multiple_items,
    "compare_user_libraries": composite.compare_user_libraries,
}

# Re-export the enhanced server objects for runtime use
mcp = _enhanced.mcp
AppContext = _enhanced.AppContext
get_client = _enhanced.get_client
app_lifespan = _enhanced.app_lifespan
main = _enhanced.main

__all__ = [
    "mcp",
    "AppContext",
    "get_client",
    "app_lifespan",
    "main",
    "TOOL_FUNCTIONS",
]


if __name__ == "__main__":
    main()
