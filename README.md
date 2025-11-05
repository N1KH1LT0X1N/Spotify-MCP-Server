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

A comprehensive Model Context Protocol (MCP) server for Spotify, enabling AI assistants to control playback, manage playlists, search music, and more

> **Note**: This is a production-ready MCP server with comprehensive documentation. If you encounter any issues during setup, check [docs/setup/troubleshooting.md](docs/setup/troubleshooting.md) - it covers all common problems and solutions.

## ⚡ Quick Start

**Want to get it looking pretty in Claude Desktop?** → [docs/setup/QUICK_SETUP.md](docs/setup/QUICK_SETUP.md) ✨

**Complete setup guide:** → [docs/setup/GET_STARTED.md](docs/setup/GET_STARTED.md) 🎵

**Detailed documentation:** → [docs/](docs/README.md) 📚

## 🎯 What Can You Do?

Ask your AI assistant:
- "Play my Discover Weekly playlist"
- "Search for jazz music and create a playlist"
- "What are my top artists this month?"
- "Add this song to my queue"
- "Show me recommendations based on chill vibes"
- "Pause playback and skip to the next track"
- "Create a playlist called 'Workout Mix' and add energetic songs"

## Features

### Current (v1.0)
- **Playback Control**: Play, pause, skip, control volume, switch devices
- **Search & Discovery**: Search tracks/albums/artists/playlists, get recommendations
- **Library Management**: Manage saved tracks
- **Playlist Operations**: Create, view, and modify playlists
- **Queue Management**: View and add to queue
- **User Info**: Get profile and listening statistics

### Coming Soon
- Audio analysis and features
- Smart playlist operations
- Podcast support
- Advanced library management (albums, shows)
- Batch operations

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

On first run, the server will open your browser to authenticate with Spotify. After granting permission, you'll be redirected to localhost, and the server will automatically save your tokens.

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

#### Search & Discovery
- `search` - Search for tracks, albums, artists, or playlists
- `get_recommendations` - Get track recommendations based on seeds

#### Library Management
- `get_saved_tracks` - Get user's saved tracks
- `save_tracks` - Save tracks to library
- `remove_saved_tracks` - Remove tracks from library
- `check_saved_tracks` - Check if tracks are saved

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

## Development

```bash
# Install in development mode
pip install -e .

# Run the server
python -m spotify_mcp.server
```

## License

MIT

## Security

See [SECURITY.md](SECURITY.md) for our security policy and best practices.

## Contributing

Contributions welcome! Please open an issue or PR.
