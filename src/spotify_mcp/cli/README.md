# Spotify MCP CLI

Beautiful command-line interface for controlling Spotify, built with Click and Rich.

## Installation

```bash
# Install with CLI support
pip install -e ".[cli]"

# Or install all optional features
pip install -e ".[all]"
```

## Usage

The CLI provides two modes of operation:

### 1. Direct Commands

Execute single commands directly:

```bash
# Show current playback status
spotify-mcp-cli status

# Control playback
spotify-mcp-cli playback play
spotify-mcp-cli playback pause
spotify-mcp-cli playback next
spotify-mcp-cli playback previous

# Set volume (0-100)
spotify-mcp-cli playback volume 50

# Search for music
spotify-mcp-cli search "bohemian rhapsody"
spotify-mcp-cli search --type artist "queen"
spotify-mcp-cli search --type album "nevermind"

# Manage devices
spotify-mcp-cli device list
spotify-mcp-cli device transfer <device-id>

# Library operations
spotify-mcp-cli library tracks
spotify-mcp-cli library save-track <track-id>

# Playlist management
spotify-mcp-cli playlist list
spotify-mcp-cli playlist show <playlist-id>
spotify-mcp-cli playlist create "My Playlist"
```

### 2. Interactive Mode

Launch an interactive shell for continuous control:

```bash
spotify-mcp-cli interactive
```

In interactive mode:
```
spotify> play
spotify> search chill vibes
spotify> next
spotify> status
spotify> exit
```

## Command Reference

### Playback Control

```bash
spotify-mcp-cli playback play [URI]       # Start/resume playback
spotify-mcp-cli playback pause            # Pause playback
spotify-mcp-cli playback next             # Skip to next track
spotify-mcp-cli playback previous         # Skip to previous track
spotify-mcp-cli playback volume <0-100>   # Set volume
spotify-mcp-cli playback shuffle <on|off|toggle>  # Control shuffle
spotify-mcp-cli playback repeat <off|track|context>  # Control repeat
spotify-mcp-cli playback seek <seconds>   # Seek to position
```

### Status

```bash
spotify-mcp-cli status                    # Show current playback
```

Displays:
- Currently playing track, artist, album
- Playback state (playing/paused)
- Progress bar with time
- Device information
- Volume, shuffle, and repeat settings

### Search

```bash
spotify-mcp-cli search <query> [options]

Options:
  -t, --type <track|artist|album|playlist|all>  Search type (default: track)
  -l, --limit <number>                          Results limit (default: 10)
```

### Device Management

```bash
spotify-mcp-cli device list               # List available devices
spotify-mcp-cli device transfer <id>      # Transfer playback to device
```

### Library

```bash
spotify-mcp-cli library tracks            # List saved tracks
spotify-mcp-cli library save-track <id>   # Save track to library
spotify-mcp-cli library remove-track <id> # Remove track from library
```

### Playlists

```bash
spotify-mcp-cli playlist list             # List your playlists
spotify-mcp-cli playlist show <id>        # Show playlist details
spotify-mcp-cli playlist create <name>    # Create new playlist
spotify-mcp-cli playlist add-track <playlist-id> <track-id>  # Add track
```

## Examples

### Quick Playback Control

```bash
# Start playing a specific track
spotify-mcp-cli playback play spotify:track:3n3Ppam7vgaVa1iaRUc9Lp

# Play a playlist
spotify-mcp-cli playback play spotify:playlist:37i9dQZF1DXcBWIGoYBM5M

# Control volume and shuffle
spotify-mcp-cli playback volume 75
spotify-mcp-cli playback shuffle on
```

### Discover Music

```bash
# Search for tracks
spotify-mcp-cli search "purple rain" --type track --limit 5

# Find artists
spotify-mcp-cli search "prince" --type artist

# Search everything
spotify-mcp-cli search "jazz" --type all
```

### Manage Library

```bash
# View your saved tracks
spotify-mcp-cli library tracks --limit 20

# Save current track (in interactive mode)
spotify> save
```

### Playlist Workflow

```bash
# Create a new playlist
spotify-mcp-cli playlist create "Summer 2024" --description "My summer vibes"

# Add tracks to it
spotify-mcp-cli playlist add-track <playlist-id> <track-id>

# View the playlist
spotify-mcp-cli playlist show <playlist-id>
```

## Interactive Mode Commands

When in interactive mode (`spotify-mcp-cli interactive`):

| Command | Description |
|---------|-------------|
| `play [uri]` | Start/resume playback |
| `pause` | Pause playback |
| `next`, `skip` | Skip to next track |
| `prev`, `previous`, `back` | Skip to previous track |
| `status` | Show current playback |
| `search <query>` | Search for tracks |
| `tracks` | List saved tracks |
| `devices` | List available devices |
| `save` | Save current track |
| `help` | Show help |
| `exit`, `quit`, `q` | Exit interactive mode |

## Features

- **Beautiful Output**: Rich formatting with colors, tables, and panels
- **Graceful Degradation**: Works even if Rich is not installed
- **Error Handling**: Clear, helpful error messages
- **Fast**: Caching ensures quick responses
- **Intuitive**: Natural command structure with helpful prompts

## Requirements

- Python 3.10+
- Spotify account (Premium for playback control)
- Spotify application credentials

## Getting Help

```bash
# General help
spotify-mcp-cli --help

# Command-specific help
spotify-mcp-cli playback --help
spotify-mcp-cli search --help

# In interactive mode
spotify> help
```

## Tips

1. **Use Tab Completion**: If your shell supports it, enable tab completion for faster commands

2. **Save Spotify URIs**: When you find something you like, copy the Spotify URI for quick access

3. **Interactive Mode**: For continuous control, use interactive mode instead of repeated commands

4. **Aliases**: Create shell aliases for frequently used commands:
   ```bash
   alias sp='spotify-mcp-cli'
   alias splay='spotify-mcp-cli playback play'
   alias spause='spotify-mcp-cli playback pause'
   alias snext='spotify-mcp-cli playback next'
   ```

## Troubleshooting

### "CLI dependencies not installed"

Install CLI dependencies:
```bash
pip install -e ".[cli]"
```

### "Authentication failed"

Check your Spotify credentials in `.env`:
```bash
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

### "Access forbidden" or "Premium required"

Some features (like playback control) require Spotify Premium.

## See Also

- [Main README](../../../README.md) - Full project documentation
- [Setup Guide](../../../docs/setup/GET_STARTED.md) - Getting started
- [API Reference](../../../docs/README.md) - Complete API documentation
