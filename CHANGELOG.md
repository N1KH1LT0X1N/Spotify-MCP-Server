# Changelog

All notable changes to the Spotify MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# Changelog

All notable changes to the Spotify MCP Server will be documented in this file.

## [1.0.4] - 2025-11-17

### Added
- **Player Control**: Get Recently Played Tracks
  - `get_recently_played`: Retrieve listening history with timestamps and context
  - Supports time-based filtering (after/before parameters)
  - Returns up to 50 recently played tracks
  - **Achievement**: 100% Spotify Web API coverage (86/86 endpoints implemented)**

### Changed
- Updated tool count from 85 to 86 across all documentation
- Enhanced Player Control category from 11 to 12 tools

## [1.0.3] - 2025-11-17

### Added

#### User Management & Social Features (6 new user tools + 2 playlist tools)
- **User Profile & Following**: Complete user management and social features
  - `get_user_profile` - Get any user's public profile by ID
  - `get_followed_artists` - Get artists followed by current user
  - `follow_artists_or_users` - Follow artists or users
  - `unfollow_artists_or_users` - Unfollow artists or users
  - `check_following_artists_or_users` - Check if current user follows artists/users
  - `check_current_user_follows_playlist` - Check if user(s) follow a playlist
  
- **Playlist Following**: Follow and unfollow playlists
  - `follow_playlist` - Follow/save a playlist to library
  - `unfollow_playlist` - Unfollow/remove a playlist from library

#### Infrastructure
- 10 new SpotifyClient API wrapper methods for user and playlist following
- Batch operations support (up to 50 artists/users)
- User profile retrieval capabilities
- Complete social graph management

### Changed
- Updated from 77 to 85 total tools (+8 tools, +10% increase)
- User Info category: 2 → 8 tools (+300% increase)
- Playlist Operations: 12 → 14 tools
- Enhanced social features and user management
- Updated documentation to reflect new tool count

## [1.0.2] - 2025-11-18

### Added

#### Show Management (7 new tools)
- **Complete Podcast Show Operations**: Full CRUD for managing podcast shows
  - `get_show` - Get detailed show information (description, publisher, episode count)
  - `get_several_shows` - Batch retrieve multiple shows
  - `get_show_episodes` - List all episodes from a show with pagination
  - `get_saved_shows` - Retrieve user's saved (followed) shows
  - `save_shows` - Follow/save shows to library
  - `remove_saved_shows` - Unfollow/remove shows from library
  - `check_saved_shows` - Check if shows are saved

#### Track Operations & Audio Analysis (5 new tools)
- **Track Information**: Get detailed track data
  - `get_track` - Get comprehensive track details (artists, album, duration, popularity)
  - `get_several_tracks` - Batch retrieve multiple tracks
  
- **Audio Analysis Features**: Advanced music analysis capabilities
  - `get_tracks_audio_features` - Get audio features for multiple tracks (tempo, energy, danceability, valence, etc.)
  - `get_track_audio_features` - Get audio features for a single track
  - `get_track_audio_analysis` - Get detailed low-level audio analysis (bars, beats, sections, segments, tatums)

#### Infrastructure
- 12 new SpotifyClient API wrapper methods
- Added shows.py tool module (7 tools)
- Added tracks.py tool module (5 tools)
- Market parameter support for regional content
- Batch operations support (up to 50 shows, 100 track audio features)

### Changed
- Updated from 65 to 77 total tools (+12 tools, +18% increase)
- Expanded from 14 to 16 categories
- Updated documentation to reflect new tool count
- Enhanced README.md with Show Management and Track Operations sections

## [1.0.1] - 2025-11-18

### Added

#### Enhanced Playlist Operations (7 new tools)
- **Advanced Playlist Management**: Complete playlist CRUD with all Spotify API features
  - `change_playlist_details` - Update playlist name, description, public/private status, collaborative mode
  - `update_playlist_items` - Reorder tracks with position and range support
  - `get_user_playlists_by_id` - Retrieve any user's public playlists
  
- **Playlist Discovery**: Browse curated and categorized playlists
  - `get_featured_playlists` - Spotify's featured playlists with country/locale filtering
  - `get_category_playlists` - Browse playlists by category (party, workout, chill, etc.)
  
- **Playlist Customization**: Visual customization features
  - `get_playlist_cover_image` - Retrieve playlist cover art in multiple sizes
  - `add_custom_playlist_cover_image` - Upload custom playlist cover (base64 JPEG, 256KB max)

#### Infrastructure
- 8 new SpotifyClient API wrapper methods for playlist operations
- Pagination support for featured and category playlists
- Base64 image validation for cover uploads
- Expanded from 58 to 65 total tools
- Playlist category now matches all Spotify Web API endpoints

### Changed
- Updated from 58 to 65 total tools
- Playlist Operations expanded from 5 to 12 tools
- Updated documentation to reflect new tool count
- Enhanced README.md playlist section

## [1.0.0] - 2025-11-17

### Added

#### New Tool Categories (12 new tools)
- **Category Browsing (2 tools)**: Browse Spotify content categories by genre, mood, and region
  - `get_several_browse_categories` - List all browse categories with pagination
  - `get_single_browse_category` - Get detailed category information
  
- **Chapter Access (2 tools)**: Navigate audiobook chapters
  - `get_chapter` - Get chapter details with resume points
  - `get_several_chapters` - Batch retrieve chapters
  
- **Episode Management (6 tools)**: Complete podcast episode CRUD operations
  - `get_episode` - Get episode details
  - `get_several_episodes` - Batch retrieve episodes
  - `get_saved_episodes` - List saved episodes
  - `save_episodes` - Add episodes to library
  - `remove_saved_episodes` - Remove episodes from library
  - `check_saved_episodes` - Check if episodes are saved
  
- **Genre Discovery (1 tool)**: Access genre seeds for recommendations
  - `get_available_genre_seeds` - Get all available genre seeds
  
- **Market Information (1 tool)**: Check Spotify availability
  - `get_available_markets` - Get available countries

#### Expanded Tool Coverage (24 new tools in existing categories)
- **Album Operations (8 tools)**: Complete album management
  - `get_album`, `get_several_albums`, `get_album_tracks`
  - `get_saved_albums`, `save_albums`, `remove_saved_albums`
  - `check_saved_albums`, `get_new_releases`
  
- **Artist Operations (5 tools)**: Artist discovery and exploration
  - `get_artist`, `get_several_artists`, `get_artist_albums`
  - `get_artist_top_tracks`, `get_artist_related_artists`
  
- **Audiobook Operations (7 tools)**: Audiobook library management
  - `get_audiobook`, `get_several_audiobooks`, `get_audiobook_chapters`
  - `get_saved_audiobooks`, `save_audiobooks`, `remove_saved_audiobooks`
  - `check_saved_audiobooks`

#### Documentation
- Comprehensive tool documentation across 58 tools
- Updated README with 14 categories breakdown
- Clean repository structure with organized docs/
- Production-ready setup guides

#### Infrastructure
- 14 new SpotifyClient API wrapper methods
- Consistent error handling across all tools
- Input validation and sanitization
- Batch operation support (up to 50 items)
- Pagination support where applicable

### Changed
- Updated from 46 to 58 total tools
- Reorganized documentation for better navigation
- Improved CONTRIBUTING.md with complete tool module list
- Enhanced STRUCTURE.md with current file counts
- Updated pyproject.toml description

### Fixed
- Security vulnerabilities in dependencies
  - Updated spotipy to 2.24.0
  - Updated python-dotenv to 1.0.1
  - Updated pydantic to 2.5.0
- Command injection risk in setup scripts
- URL validation in authentication
- Git Bash path resolution issues

### Security
- Comprehensive security audit completed
- All vulnerabilities addressed
- Input sanitization added
- OAuth token security enhanced
- Security checklist documentation added

## [0.1.0] - 2025-11-05

### Added
- Initial release with 22 core tools
- Playback Control (11 tools)
- Search & Discovery (2 tools)
- Library Management (4 tools)
- Playlist Operations (5 tools)
- Queue Management (2 tools)
- User Info (2 tools)
- OAuth authentication flow
- Claude Desktop integration
- Basic documentation
- Test suite (69 tests)

### Infrastructure
- MCP protocol implementation
- SpotifyClient wrapper
- Error handling framework
- Development scripts
- CI/CD workflows

---

## Version History Summary

| Version | Date | Tools | Categories | Status |
|---------|------|-------|------------|--------|
| **1.0.3** | 2025-11-18 | 85 | 16 | Latest |
| 1.0.2 | 2025-11-18 | 77 | 16 | Shows & Tracks |
| 1.0.1 | 2025-11-18 | 65 | 14 | Playlist enhancements |
| 1.0.0 | 2025-11-17 | 58 | 14 | Production-ready |
| 0.1.0 | 2025-11-05 | 22 | 6 | Initial release |

---

## Upgrade Guide

### From 1.0.2 to 1.0.3

No breaking changes! All existing tools remain unchanged. Simply pull the latest code to access 8 new user and playlist tools.

**New capabilities available:**
- Get any user's public profile
- Follow/unfollow artists and users
- Get followed artists with pagination
- Check following status for artists/users
- Follow/unfollow playlists
- Check if users follow playlists

**Action required:**
- None! All new tools are automatically available after update
- Optionally review new user management features in README.md

### From 1.0.1 to 1.0.2

No breaking changes! All existing tools remain unchanged. Simply pull the latest code to access 12 new show and track tools.

**New capabilities available:**
- Complete podcast show management (browse, save, get episodes)
- Track information retrieval (single and batch)
- Audio analysis features (tempo, energy, danceability, valence, etc.)
- Detailed audio analysis (bars, beats, sections, segments)

**Action required:**
- None! All new tools are automatically available after update
- Optionally review new show and track features in README.md

### From 1.0.0 to 1.0.1

No breaking changes! All existing tools remain unchanged. Simply pull the latest code to access 7 new playlist tools.

**New playlist capabilities available:**
- Update playlist details (name, description, public/private)
- Reorder playlist tracks by position
- Browse featured playlists (Spotify curated)
- Browse category playlists (by genre/mood)
- Get playlist cover images
- Upload custom playlist covers
- Get any user's public playlists

**Action required:**
- None! All new tools are automatically available after update
- Optionally review new playlist features in README.md

### From 0.1.0 to 1.0.0

No breaking changes! All existing tools remain unchanged. Simply pull the latest code to access 36 new tools.

**New capabilities available:**
- Album management (8 tools)
- Artist exploration (5 tools)
- Audiobook library (7 tools)
- Category browsing (2 tools)
- Chapter navigation (2 tools)
- Episode management (6 tools)
- Genre discovery (1 tool)
- Market information (1 tool)

**Action required:**
- None! All new tools are automatically available after update
- Optionally review new features in README.md
- Check updated documentation in docs/

---

## Future Releases

See [ROADMAP.md](docs/development/roadmap.md) for planned features.

**Upcoming in v1.1.0:**
- Audio Analysis tools
- Show Management
- Recently Played history

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute to future releases.

---

[1.0.0]: https://github.com/N1KH1LT0X1N/Spotify-MCP-Server/releases/tag/v1.0.0
[0.1.0]: https://github.com/N1KH1LT0X1N/Spotify-MCP-Server/releases/tag/v0.1.0
