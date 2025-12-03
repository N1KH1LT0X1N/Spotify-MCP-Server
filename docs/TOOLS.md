# 🛠️ Tool Reference

> **Total:** 75 tools (69 standard + 6 composite)

---

## 🎵 Playback Control (12 tools)

| Tool | Description |
|------|-------------|
| `play` | Start playback (track, album, playlist, or resume) |
| `pause` | Pause current playback |
| `skip_next` | Skip to next track |
| `skip_previous` | Skip to previous track |
| `get_current_playback` | Get current playback state |
| `get_available_devices` | List Spotify Connect devices |
| `transfer_playback` | Switch playback to different device |
| `set_volume` | Set volume (0-100) |
| `set_shuffle` | Toggle shuffle mode |
| `set_repeat` | Set repeat (track/context/off) |
| `seek_to_position` | Seek to position in track |
| `get_recently_played` | Get recently played tracks |

---

## 🔍 Search (1 tool)

| Tool | Description |
|------|-------------|
| `search` | Search tracks, albums, artists, playlists, shows, episodes |

---

## 💾 Library - Tracks (4 tools)

| Tool | Description |
|------|-------------|
| `get_saved_tracks` | Get user's liked songs |
| `save_tracks` | Like tracks |
| `remove_saved_tracks` | Unlike tracks |
| `check_saved_tracks` | Check if tracks are liked |

---

## 📀 Albums (8 tools)

| Tool | Description |
|------|-------------|
| `get_album` | Get album details |
| `get_several_albums` | Get multiple albums |
| `get_album_tracks` | Get tracks from album |
| `get_saved_albums` | Get saved albums |
| `save_albums` | Save albums to library |
| `remove_saved_albums` | Remove albums from library |
| `check_saved_albums` | Check if albums are saved |
| `get_new_releases` | Get new album releases |

---

## 🎤 Artists (4 tools)

| Tool | Description |
|------|-------------|
| `get_artist` | Get artist details |
| `get_several_artists` | Get multiple artists |
| `get_artist_albums` | Get artist's discography |
| `get_artist_top_tracks` | Get artist's top tracks |

---

## 🎶 Playlists (12 tools)

| Tool | Description |
|------|-------------|
| `get_user_playlists` | Get current user's playlists |
| `get_playlist` | Get playlist details and tracks |
| `create_playlist` | Create new playlist |
| `add_tracks_to_playlist` | Add tracks to playlist |
| `remove_tracks_from_playlist` | Remove tracks from playlist |
| `change_playlist_details` | Update name/description |
| `update_playlist_items` | Reorder playlist tracks |
| `get_playlist_cover_image` | Get playlist cover |
| `add_custom_playlist_cover_image` | Upload custom cover |
| `get_user_playlists_by_id` | Get another user's playlists |
| `follow_playlist` | Follow a playlist |
| `unfollow_playlist` | Unfollow a playlist |

---

## ⏯️ Queue (2 tools)

| Tool | Description |
|------|-------------|
| `get_queue` | Get current queue |
| `add_to_queue` | Add track to queue |

---

## 👤 User (8 tools)

| Tool | Description |
|------|-------------|
| `get_current_user` | Get current user's profile |
| `get_top_items` | Get user's top tracks/artists |
| `get_user_profile` | Get any user's public profile |
| `get_followed_artists` | Get followed artists |
| `follow_artists_or_users` | Follow artists/users |
| `unfollow_artists_or_users` | Unfollow artists/users |
| `check_following_artists_or_users` | Check follow status |
| `check_current_user_follows_playlist` | Check playlist follow |

---

## 🏷️ Categories (2 tools)

| Tool | Description |
|------|-------------|
| `get_several_browse_categories` | Get browse categories |
| `get_single_browse_category` | Get category details |

---

## 🎙️ Episodes (6 tools)

| Tool | Description |
|------|-------------|
| `get_episode` | Get episode details |
| `get_several_episodes` | Get multiple episodes |
| `get_saved_episodes` | Get saved episodes |
| `save_episodes` | Save episodes |
| `remove_saved_episodes` | Remove saved episodes |
| `check_saved_episodes` | Check if episodes are saved |

---

## 📻 Shows (7 tools)

| Tool | Description |
|------|-------------|
| `get_show` | Get show/podcast details |
| `get_several_shows` | Get multiple shows |
| `get_show_episodes` | Get episodes from show |
| `get_saved_shows` | Get saved shows |
| `save_shows` | Save shows |
| `remove_saved_shows` | Remove saved shows |
| `check_saved_shows` | Check if shows are saved |

---

## 🎵 Tracks (2 tools)

| Tool | Description |
|------|-------------|
| `get_track` | Get track details |
| `get_several_tracks` | Get multiple tracks |

---

## 🌍 Markets (1 tool)

| Tool | Description |
|------|-------------|
| `get_available_markets` | Get available Spotify markets |

---

## 🔗 Composite Tools (6 tools)

*Multi-step operations combined for convenience*

| Tool | Description |
|------|-------------|
| `create_playlist_with_tracks` | Create playlist and add tracks in one call |
| `get_artist_full_profile` | Get artist + top tracks + albums at once |
| `search_and_create_playlist` | Search and create playlist from results |
| `get_listening_summary` | Get comprehensive listening stats |
| `save_multiple_items` | Bulk save tracks/albums/follow artists |
| `compare_user_libraries` | Compare libraries with another user |

---

## ⚠️ Deprecated (Removed)

These tools were removed due to Spotify API deprecations (Nov 27, 2024):

| Tool | Reason |
|------|--------|
| `get_track_audio_features` | API deprecated |
| `get_tracks_audio_features` | API deprecated |
| `get_track_audio_analysis` | API deprecated |
| `get_recommendations` | API deprecated |
| `get_available_genre_seeds` | API deprecated |
| `get_artist_related_artists` | API deprecated |
| `get_featured_playlists` | API deprecated |
| `get_category_playlists` | API deprecated |
| All audiobook tools (8) | Requires Extended Quota |
| All chapter tools (2) | Requires Extended Quota |
