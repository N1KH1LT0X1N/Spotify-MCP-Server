# Spotify API Endpoint Test Report

**Last Updated:** December 3, 2025  
**Version:** 2.0.0 (Post-cleanup)

## Summary

| Status | Count |
|--------|-------|
| ✅ WORKING | 69 |
| ⚠️ DEPRECATED (Removed) | 17 |
| **TOTAL ACTIVE** | **69** |

## Deprecation Notice

On **November 27, 2024**, Spotify deprecated several API endpoints for applications in Development Mode. These endpoints now return 403/404 errors and have been removed from this MCP server.

### Removed Endpoints (17 tools)

| Tool | Category | Reason |
|------|----------|--------|
| `get_track_audio_features` | Tracks | Spotify deprecated Nov 2024 |
| `get_tracks_audio_features` | Tracks | Spotify deprecated Nov 2024 |
| `get_track_audio_analysis` | Tracks | Spotify deprecated Nov 2024 |
| `get_recommendations` | Search | Spotify deprecated Nov 2024 |
| `get_available_genre_seeds` | Genres | Used only with recommendations |
| `get_artist_related_artists` | Artists | Spotify deprecated Nov 2024 |
| `get_featured_playlists` | Playlists | Spotify deprecated Nov 2024 |
| `get_category_playlists` | Playlists | Spotify deprecated Nov 2024 |
| `get_audiobook` | Audiobooks | Requires Extended Quota Mode |
| `get_several_audiobooks` | Audiobooks | Requires Extended Quota Mode |
| `get_audiobook_chapters` | Audiobooks | Requires Extended Quota Mode |
| `get_saved_audiobooks` | Audiobooks | spotipy missing method |
| `save_audiobooks` | Audiobooks | spotipy missing method |
| `remove_saved_audiobooks` | Audiobooks | spotipy missing method |
| `check_saved_audiobooks` | Audiobooks | spotipy missing method |
| `get_chapter` | Chapters | spotipy missing method |
| `get_several_chapters` | Chapters | spotipy missing method |

## ✅ Working Endpoints (69 tools)

### Playback Control (12 tools)
| Tool | Status | Notes |
|------|--------|-------|
| `play` | ✅ | Requires Premium + active device |
| `pause` | ✅ | Requires Premium + active device |
| `skip_next` | ✅ | Requires Premium + active device |
| `skip_previous` | ✅ | Requires Premium + active device |
| `get_current_playback` | ✅ | |
| `get_available_devices` | ✅ | |
| `transfer_playback` | ✅ | Requires Premium |
| `set_volume` | ✅ | Requires Premium (may fail on some devices) |
| `set_shuffle` | ✅ | Requires Premium |
| `set_repeat` | ✅ | Requires Premium |
| `seek_to_position` | ✅ | Requires Premium |
| `get_recently_played` | ✅ | |

### Search (1 tool)
| Tool | Status | Notes |
|------|--------|-------|
| `search` | ✅ | Search tracks, albums, artists, playlists |

### Library (4 tools)
| Tool | Status | Notes |
|------|--------|-------|
| `get_saved_tracks` | ✅ | |
| `save_tracks` | ✅ | |
| `remove_saved_tracks` | ✅ | |
| `check_saved_tracks` | ✅ | |

### Albums (8 tools)
| Tool | Status | Notes |
|------|--------|-------|
| `get_album` | ✅ | |
| `get_several_albums` | ✅ | |
| `get_album_tracks` | ✅ | |
| `get_saved_albums` | ✅ | |
| `save_albums` | ✅ | |
| `remove_saved_albums` | ✅ | |
| `check_saved_albums` | ✅ | |
| `get_new_releases` | ✅ | |

### Artists (4 tools)
| Tool | Status | Notes |
|------|--------|-------|
| `get_artist` | ✅ | |
| `get_several_artists` | ✅ | |
| `get_artist_albums` | ✅ | |
| `get_artist_top_tracks` | ✅ | |

### Playlists (12 tools)
| Tool | Status | Notes |
|------|--------|-------|
| `get_user_playlists` | ✅ | |
| `get_user_playlists_by_id` | ✅ | |
| `get_playlist` | ✅ | |
| `create_playlist` | ✅ | |
| `change_playlist_details` | ✅ | |
| `add_tracks_to_playlist` | ✅ | |
| `remove_tracks_from_playlist` | ✅ | |
| `update_playlist_items` | ✅ | |
| `get_playlist_cover_image` | ✅ | |
| `add_custom_playlist_cover_image` | ✅ | Requires ugc-image-upload scope |
| `follow_playlist` | ✅ | |
| `unfollow_playlist` | ✅ | |

### Queue (2 tools)
| Tool | Status | Notes |
|------|--------|-------|
| `get_queue` | ✅ | Requires active playback |
| `add_to_queue` | ✅ | Requires Premium + active device |

### User (8 tools)
| Tool | Status | Notes |
|------|--------|-------|
| `get_current_user` | ✅ | |
| `get_user_profile` | ✅ | |
| `get_top_items` | ✅ | |
| `get_followed_artists` | ✅ | |
| `follow_artists_or_users` | ✅ | |
| `unfollow_artists_or_users` | ✅ | |
| `check_following_artists_or_users` | ✅ | |
| `check_current_user_follows_playlist` | ✅ | |

### Categories (2 tools)
| Tool | Status | Notes |
|------|--------|-------|
| `get_several_browse_categories` | ✅ | |
| `get_single_browse_category` | ✅ | |

### Episodes (6 tools)
| Tool | Status | Notes |
|------|--------|-------|
| `get_episode` | ✅ | Requires valid episode ID |
| `get_several_episodes` | ✅ | |
| `get_saved_episodes` | ✅ | |
| `save_episodes` | ✅ | |
| `remove_saved_episodes` | ✅ | |
| `check_saved_episodes` | ✅ | |

### Shows (7 tools)
| Tool | Status | Notes |
|------|--------|-------|
| `get_show` | ✅ | |
| `get_several_shows` | ✅ | |
| `get_show_episodes` | ✅ | |
| `get_saved_shows` | ✅ | |
| `save_shows` | ✅ | |
| `remove_saved_shows` | ✅ | |
| `check_saved_shows` | ✅ | |

### Tracks (2 tools)
| Tool | Status | Notes |
|------|--------|-------|
| `get_track` | ✅ | |
| `get_several_tracks` | ✅ | |

### Markets (1 tool)
| Tool | Status | Notes |
|------|--------|-------|
| `get_available_markets` | ✅ | |

## Tool Categories Summary

| Category | Count | Status |
|----------|-------|--------|
| Playback | 12 | ✅ All working |
| Search | 1 | ✅ Working |
| Library | 4 | ✅ All working |
| Albums | 8 | ✅ All working |
| Artists | 4 | ✅ All working |
| Playlists | 12 | ✅ All working |
| Queue | 2 | ✅ All working |
| User | 8 | ✅ All working |
| Categories | 2 | ✅ All working |
| Episodes | 6 | ✅ All working |
| Shows | 7 | ✅ All working |
| Tracks | 2 | ✅ All working |
| Markets | 1 | ✅ All working |
| **Total** | **69** | **✅ All working** |

## Known Limitations

1. **Playback controls** require Spotify Premium and an active device
2. **set_volume** may not work on all devices (web player limitation)
3. **get_queue** requires active playback to return results
4. **Episodes** require valid podcast episode IDs

## References

- [Spotify API Deprecation Notice (Nov 27, 2024)](https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api)
- [Spotify Web API Documentation](https://developer.spotify.com/documentation/web-api)
