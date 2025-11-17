# Contributing to Spotify MCP Server

**Welcome!** 🎵 Whether you're fixing a bug, adding features, or improving docs—your contributions make this project better for everyone.

This guide walks you through adding new tools and features to the Spotify MCP Server. It's designed to be clear and practical.

## 🚀 Development Setup

```bash
# Clone and install in development mode
git clone <your-repo>
cd spotify-mcp
pip install -e ".[dev]"  # Includes test dependencies

# Verify everything works
python scripts/verify_setup.py

# Run tests
pytest
```

## Project Structure

```
spotify-mcp/
├── src/spotify_mcp/
│   ├── server.py          # Main MCP server
│   ├── auth.py            # OAuth authentication
│   ├── spotify_client.py  # API wrapper with error handling
│   └── tools/             # Tool implementations
│       ├── playback.py    # Playback control
│       ├── search.py      # Search & recommendations
│       ├── library.py     # Library management (tracks)
│       ├── albums.py      # Album operations
│       ├── artists.py     # Artist operations
│       ├── audiobooks.py  # Audiobook operations
│       ├── categories.py  # Category browsing
│       ├── chapters.py    # Audiobook chapters
│       ├── episodes.py    # Podcast episodes
│       ├── genres.py      # Genre discovery
│       ├── markets.py     # Market information
│       ├── playlists.py   # Playlist operations
│       ├── queue.py       # Queue management
│       └── user.py        # User info
```

## Adding New Tools

### 1. Create Tool Function

Add your tool function to the appropriate module in `tools/`:

```python
def your_new_tool(client: SpotifyClient, param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    Description of what your tool does.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (optional)
    
    Returns:
        Description of return value
    """
    # Validate inputs
    if not param1:
        raise ValueError("param1 cannot be empty")
    
    # Call Spotify API through client
    result = client.some_api_method(param1, param2)
    
    # Format and return response
    return {
        "success": True,
        "data": result,
        # ... format as needed
    }
```

### 2. Add Tool Definition

Add the MCP tool definition to the `TOOLS` list in the same file:

```python
YOUR_TOOLS = [
    {
        "name": "your_new_tool",
        "description": "Clear description of what the tool does",
        "inputSchema": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Description for the AI"
                },
                "param2": {
                    "type": "integer",
                    "description": "Optional parameter",
                    "default": 10
                }
            },
            "required": ["param1"]  # Only required params
        }
    }
]
```

### 3. Register in Server

In `server.py`:

1. Import your function and tool definitions:
```python
from spotify_mcp.tools.your_module import (
    YOUR_TOOLS, your_new_tool
)
```

2. Add to `TOOL_FUNCTIONS` dict:
```python
TOOL_FUNCTIONS = {
    # ... existing tools
    "your_new_tool": your_new_tool,
}
```

3. Add to `list_tools()`:
```python
all_tools = (
    PLAYBACK_TOOLS +
    # ... other tools
    YOUR_TOOLS
)
```

### 4. Add Client Method (if needed)

If you need a new Spotify API endpoint, add it to `spotify_client.py`:

```python
def your_api_method(self, param1: str, param2: int):
    """Call new Spotify API endpoint."""
    return self._handle_api_call(
        self.sp.your_spotify_method,
        param1=param1,
        param2=param2
    )
```

## Phase 2 Features to Implement

### Audio Analysis Tools
- `get_audio_features` - Get audio features for tracks
- `get_audio_analysis` - Get detailed audio analysis
- `analyze_playlist` - Analyze characteristics of a playlist

### Advanced Library - Shows & Podcasts
- `get_saved_shows` - Get saved podcasts
- `save_shows` / `remove_saved_shows` - Manage saved podcasts

### Follow Management
- `get_followed_artists` - Get followed artists
- `follow_artists` / `unfollow_artists` - Manage follows
- `check_following` - Check if following artists/users

### Smart Operations
- `create_playlist_from_features` - Create playlist based on audio features
- `merge_playlists` - Combine multiple playlists
- `sort_playlist` - Sort by various attributes
- `find_duplicates` - Find duplicate tracks

### Podcast Support
- `search_shows` - Search for podcasts
- `get_show_episodes` - Get episodes of a show
- `save_episodes` / `remove_episodes` - Manage saved episodes

### Recently Played
- `get_recently_played` - Get recently played tracks

**Note:** Album operations (get_album, get_several_albums, get_album_tracks, get_saved_albums, save_albums, remove_saved_albums, check_saved_albums, get_new_releases) are now fully implemented in Phase 1!

## Best Practices

### Error Handling
- Use descriptive error messages
- Validate inputs before API calls
- Let `spotify_client._handle_api_call` handle API errors

### Response Formatting
- Return consistent dict structures
- Include relevant metadata (totals, pagination, etc.)
- Format timestamps, durations clearly
- Extract nested data to flat structure when sensible

### Documentation
- Write clear docstrings
- Include examples in docstrings
- Update README when adding major features
- Comment complex logic

### Testing
Before submitting:
```bash
# Verify imports work
python -c "from spotify_mcp.tools.your_module import your_new_tool"

# Run the server
python -m spotify_mcp.server

# Test your tool through Claude or directly
```

## Code Style

- Follow PEP 8
- Use type hints
- Keep functions focused and small
- Use descriptive variable names
- Add comments for non-obvious logic

## Spotify API Reference

- [Web API Reference](https://developer.spotify.com/documentation/web-api/reference/)
- [Spotipy Documentation](https://spotipy.readthedocs.io/)

## Common Patterns

### Pagination
```python
results = client.some_method(limit=limit, offset=offset)
items = results.get("items", [])
total = results.get("total", 0)

return {
    "items": formatted_items,
    "total": total,
    "limit": limit,
    "offset": offset,
    "has_more": offset + limit < total
}
```

### ID/URI Handling
```python
# Extract ID from URI if needed
item_id = item_id.split(":")[-1] if ":" in item_id else item_id
```

### Batch Operations
```python
if len(items) > 50:
    raise ValueError("Cannot process more than 50 items at once")
```

## Questions?

Open an issue or discussion on GitHub!
