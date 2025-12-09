# 📡 API Reference

## MCP Resources (10)

Resources provide real-time data access via `spotify://` URIs.

| URI | Description |
|-----|-------------|
| `spotify://playback/current` | Current playback state (track, device, progress) |
| `spotify://queue` | Current playback queue |
| `spotify://library/saved-tracks` | User's liked songs |
| `spotify://library/recent` | Recently played tracks |
| `spotify://playlists` | User's playlists |
| `spotify://devices` | Available Spotify Connect devices |
| `spotify://user/profile` | Current user's profile |
| `spotify://user/top-tracks` | User's top tracks (medium term) |
| `spotify://user/top-artists` | User's top artists |
| `spotify://search/results` | Recent search results |

---

## Architecture

### Server Entry Points

The server can be started in multiple ways:

```bash
# Direct module execution (recommended)
python -m spotify_mcp.spotify_server

# Using installed command (after pip install -e .)
spotify-mcp

# Compatibility shim for legacy tests
python -m spotify_mcp.server
```

### Architecture Overview

```
spotify_server.py (3,215 lines)
├── FastMCP v3.0 server instance
├── 75 @mcp.tool() decorated async functions
├── 10 @mcp.resource() handlers
├── AppContext with SpotifyClient
└── app_lifespan() for startup/shutdown

server.py (157 lines)
├── Compatibility shim for tests
├── TOOL_FUNCTIONS dict (75 tools)
└── Re-exports main() and mcp

tools/ (16 modules)
├── playback.py (12 tools)
├── playlists.py (12 tools)
├── albums.py (8 tools)
├── user.py (8 tools)
├── shows.py (7 tools)
├── episodes.py (6 tools)
├── composite.py (6 tools)
└── ... (7 more modules)
```

### Tool Organization

- **Individual tools (69)**: Sync implementations in `src/spotify_mcp/tools/` modules
- **Composite tools (6)**: Multi-step operations in `tools/composite.py`
- **FastMCP wrappers**: Async `@mcp.tool()` decorators in `spotify_server.py`
- **Compatibility layer**: `TOOL_FUNCTIONS` dict in `server.py` for legacy tests
- **Context injection**: FastMCP Context provides SpotifyClient access

---

## Authentication

### Required Scopes

```
user-read-playback-state
user-modify-playback-state
user-read-currently-playing
user-read-recently-played
user-top-read
user-library-read
user-library-modify
playlist-read-private
playlist-read-collaborative
playlist-modify-public
playlist-modify-private
user-follow-read
user-follow-modify
user-read-private
user-read-email
ugc-image-upload
user-read-playback-position
```

### Token Flow

1. User authorizes via Spotify OAuth
2. Server receives authorization code
3. Code exchanged for access + refresh tokens
4. Tokens stored in environment/keyring
5. Access token auto-refreshed when expired (1 hour)

---

## Rate Limits

Spotify enforces rate limits per app:

| Limit Type | Value |
|------------|-------|
| Requests per 30 seconds | ~180 |
| Retry-After header | Provided on 429 |
| Backoff strategy | Exponential with jitter |

The server automatically handles rate limits with retry logic.

---

## Error Codes

| HTTP Code | Meaning | Recovery |
|-----------|---------|----------|
| 400 | Bad Request | Check parameters |
| 401 | Unauthorized | Re-authenticate |
| 403 | Forbidden | Check permissions/Premium |
| 404 | Not Found | Verify resource ID |
| 429 | Rate Limited | Wait and retry |
| 500+ | Server Error | Retry later |

---

## Caching

Built-in intelligent caching reduces API calls:

| Data Type | TTL | Example |
|-----------|-----|---------|
| Static (tracks, albums, artists) | 24 hours | Track metadata |
| Semi-static (playlists, library) | 3-5 minutes | User playlists |
| Dynamic (playback, queue) | 10-30 seconds | Current track |

Cache is memory-based by default. Optional Redis support for distributed caching.
