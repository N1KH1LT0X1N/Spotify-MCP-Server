# 🎵 Spotify MCP Server

<div align="center">
  <img src="icon.svg" alt="Spotify MCP Server" width="128" height="128">
  <br><br>
</div>

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io)
[![Spotify API](https://img.shields.io/badge/Spotify-Web%20API-1DB954.svg)](https://developer.spotify.com/documentation/web-api)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Transform your AI assistant into a Spotify DJ.** Natural language commands become instant music control—search songs, manage playlists, control playback, discover new artists, and explore your entire library through simple conversation.

> **Production-ready** with 86 tools (100% Spotify API coverage), comprehensive docs, and battle-tested reliability. Setup in 5 minutes. Issues? Check [troubleshooting](docs/setup/troubleshooting.md) for instant solutions.

## ⚡ Quick Start

**New here?** → Run `python tools/setup_guide.py` for interactive setup! 🎯

**Want Claude Desktop config?** → [docs/setup/QUICK_SETUP.md](docs/setup/QUICK_SETUP.md) ✨

**Prefer step-by-step?** → [docs/setup/GET_STARTED.md](docs/setup/GET_STARTED.md) 📖

**All documentation:** → [docs/](docs/README.md) 📚

## 🎯 What You Can Do

Just talk naturally to your AI:

**🎵 Control Your Music**
- "Play my Discover Weekly playlist"
- "Pause and skip to the next track"
- "Turn the volume down to 40%"

**🔍 Discover & Explore**
- "Find me some chill jazz tracks"
- "Show me albums by Radiohead"
- "What are similar artists to Tame Impala?"

**📚 Manage Your Library**
- "Save this album to my library"
- "What are my top artists this month?"
- "Create a playlist called 'Workout Mix'"

**💡 Get Smart**
- "Recommend songs based on chill vibes"
- "Show me new album releases"
- "Add this to my queue for later"

## ✨ Features

### 🚀 v1.0 - Production Ready (86 Tools - 100% API Coverage)

**🎵 Playback Control** (12 tools)
Full control over your music: play, pause, skip, volume, shuffle, repeat, seek, device switching, recently played history

**🔍 Search & Discovery** (2 tools)
Find anything on Spotify and get personalized recommendations

**💾 Library Management** (4 tools)
Save, remove, and check your favorite tracks

**📀 Album Operations** (8 tools)
Explore albums, save to library, discover new releases

**🎤 Artist Operations** (5 tools)
Dive deep into artist profiles, discographies, and related artists

**📚 Audiobook Operations** (7 tools)
Browse, save, and manage audiobooks and chapters

**🏷️ Category Browsing** (2 tools)
Explore Spotify content categories by genre, mood, and region

**📖 Chapter Access** (2 tools)
Navigate audiobook chapters with detailed information

**🎙️ Episode Management** (6 tools)
Browse, save, and manage podcast episodes

**🎸 Genre Discovery** (1 tool)
Get available genre seeds for music recommendations

**🌍 Market Information** (1 tool)
Check Spotify availability by country

**🎶 Playlist Operations** (14 tools)
Create, modify, manage, and discover playlists—update details, reorder tracks, upload covers, follow/unfollow, browse featured and category playlists

**⏯️ Queue Management** (2 tools)
View and control what plays next

**👤 User Info** (8 tools)
Access profiles, follow/unfollow artists and users, check followings, and get listening statistics

**📻 Show Management** (7 tools)
Browse podcasts, save shows, get episodes

**🎵 Track Operations** (5 tools)
Get track details, audio features, and audio analysis

### 🔮 Coming in Future Releases

**Power Features**
- Batch operations for efficiency
- Advanced library filtering and organization
- Social features (follow/unfollow artists and users)

## Prerequisites

- Python 3.10 or higher
- A Spotify account (Premium required for playback control)
- Spotify Developer account

## Setup

### 1. Create a Spotify Application

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create app"
4. Fill in the details:
   - **App name**: Whatever you like (e.g., "My MCP Server")
   - **App description**: "MCP server for Spotify control"
   - **Redirect URI**: `http://127.0.0.1:8888/callback` ⚠️ **Must use 127.0.0.1, not localhost**
   - **APIs used**: Select "Web API"
5. Agree to terms and click "Save"
6. Click "Settings" to view your **Client ID** and **Client Secret**

### 2. Install the MCP Server

```bash
cd spotify-mcp
pip install -e .
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

### 4. Authenticate with Spotify

On first run, the server will open your browser to authenticate with Spotify. After granting permission, you'll be redirected to `http://127.0.0.1:8888/callback`, and the server will automatically save your tokens.

## Usage

### With Claude Desktop

**Quick Setup:** See [docs/setup/QUICK_SETUP.md](docs/setup/QUICK_SETUP.md) for copy-paste configuration! 🎵

**Detailed Guide:** See [docs/setup/CLAUDE_DESKTOP_SETUP.md](docs/setup/CLAUDE_DESKTOP_SETUP.md)

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "spotify": {
      "command": "python",
      "args": ["-m", "spotify_mcp.server"],
      "env": {
        "SPOTIFY_CLIENT_ID": "your_client_id",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback"
      },
      "icon": "C:\\full\\path\\to\\spotify_mcp\\icon.svg"
    }
  }
}
```

**Note:** Add the `icon` property with the full path to `icon.svg` to display the beautiful Spotify icon in Claude Desktop! 🎵

### Available Tools

#### Playback Control
- `play` - Play a track, album, or playlist
- `pause` - Pause playback
- `skip_next` - Skip to next track
- `skip_previous` - Skip to previous track
- `get_current_playback` - Get current playback state
- `get_available_devices` - List available Spotify Connect devices
- `transfer_playback` - Switch playback to a different device
- `set_volume` - Set playback volume
- `set_shuffle` - Toggle shuffle mode
- `set_repeat` - Set repeat mode
- `seek_to_position` - Seek to position in track

#### Search & Discovery
- `search` - Search for tracks, albums, artists, or playlists
- `get_recommendations` - Get track recommendations based on seeds

#### Library Management - Tracks
- `get_saved_tracks` - Get user's saved tracks
- `save_tracks` - Save tracks to library
- `remove_saved_tracks` - Remove tracks from library
- `check_saved_tracks` - Check if tracks are saved

#### Album Operations
- `get_album` - Get album details and tracks
- `get_several_albums` - Get multiple albums efficiently
- `get_album_tracks` - Get tracks from an album
- `get_saved_albums` - Get user's saved albums
- `save_albums` - Save albums to library
- `remove_saved_albums` - Remove albums from library
- `check_saved_albums` - Check if albums are saved
- `get_new_releases` - Get new album releases

#### Artist Operations
- `get_artist` - Get artist details, genres, and popularity
- `get_several_artists` - Get multiple artists efficiently
- `get_artist_albums` - Get artist's albums, singles, and compilations
- `get_artist_top_tracks` - Get artist's top tracks by market
- `get_artist_related_artists` - Get similar artists

#### Audiobook Operations
- `get_audiobook` - Get audiobook details, chapters, authors, and narrators
- `get_several_audiobooks` - Get multiple audiobooks efficiently
- `get_audiobook_chapters` - Get chapters from an audiobook
- `get_saved_audiobooks` - Get user's saved audiobooks
- `save_audiobooks` - Save audiobooks to library
- `remove_saved_audiobooks` - Remove audiobooks from library
- `check_saved_audiobooks` - Check if audiobooks are saved

#### Playlist Operations
- `get_user_playlists` - Get user's playlists
- `get_playlist` - Get playlist details and tracks
- `create_playlist` - Create a new playlist
- `add_tracks_to_playlist` - Add tracks to a playlist
- `remove_tracks_from_playlist` - Remove tracks from a playlist

#### Queue Management
- `get_queue` - Get the current queue
- `add_to_queue` - Add a track to the queue

#### User Info
- `get_current_user` - Get current user's profile
- `get_top_items` - Get user's top tracks or artists

## Troubleshooting

For detailed troubleshooting, see [docs/setup/troubleshooting.md](docs/setup/troubleshooting.md).

### Quick Fixes

**"ModuleNotFoundError: No module named 'spotify_mcp'"**
- Set PYTHONPATH: `$env:PYTHONPATH = "src"` (Windows) or `export PYTHONPATH="src"` (Linux/Mac)
- For Claude Desktop, add `"PYTHONPATH": "path/to/src"` in the env section

**"ERR_CONNECTION_REFUSED" after Spotify authorization**
- This is NORMAL! The redirect URI `http://127.0.0.1:8888/callback` is intentionally not listening
- Copy the full URL from your browser's address bar (including `?code=...`) and paste it back when prompted

**Authentication prompts breaking Claude Desktop**
- Make sure you have the latest version of `src/spotify_mcp/auth.py` (outputs to stderr, not stdout)

**Tokens not saving**
- Verify `.env` file exists in project root
- Run `python test_auth.py` to test authentication (now using 127.0.0.1)

**"Invalid redirect URI" errors**
- Spotify requires explicit IPv4: `http://127.0.0.1:8888/callback`
- Update both `.env` and Spotify Developer Dashboard
- **Do not use `localhost`** - use `127.0.0.1` instead

### Common Issues

- **No Active Device**: Open Spotify on any device to make it available for playback control
- **Premium Required**: Playback control (play, pause, skip) requires Spotify Premium
- **Rate Limits**: The server automatically handles Spotify's rate limits with exponential backoff

For more details and solutions, see [docs/setup/troubleshooting.md](docs/setup/troubleshooting.md).

## 🚀 Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Check code quality
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔒 Security

We take security seriously. See [SECURITY.md](SECURITY.md) for:
- Security best practices
- Token storage and encryption
- Enterprise security features
- How to report vulnerabilities

## 🤝 Contributing

Contributions are welcome! Whether it's:
- 🐛 Bug fixes
- ✨ New features
- 📖 Documentation improvements
- 🎨 UI/UX enhancements

See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

## 🆘 Support

**Having issues?**
- 📖 Check [troubleshooting guide](docs/setup/troubleshooting.md)
- 🔍 Search [existing issues](https://github.com/N1KH1LT0X1N/Spotify-MCP-Server/issues)
- 💬 Open a [new issue](https://github.com/N1KH1LT0X1N/Spotify-MCP-Server/issues/new)

**Want to help?**
- ⭐ Star this repo
- 🍴 Fork and contribute
- 📢 Share with others

---

<div align="center">
  
**Made with 🎵 for the AI + Music community**

[Documentation](docs/README.md) • [Contributing](CONTRIBUTING.md) • [Security](SECURITY.md) • [License](LICENSE)

</div>
