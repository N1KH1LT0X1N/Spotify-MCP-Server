# 📡 API Reference

## MCP Resources (8)

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

---

## MCP Prompts (8)

Pre-built conversation templates for common workflows.

| Prompt | Description | Arguments |
|--------|-------------|-----------|
| `discover_new_music` | Find new music based on preferences | `mood` (optional) |
| `create_playlist` | Create custom themed playlist | `theme` (optional) |
| `whats_playing` | Get current playback info | - |
| `control_playback` | Control playback with commands | `action` (optional) |
| `manage_library` | Organize music library | `task` (optional) |
| `find_similar` | Find similar music | `reference` (required) |
| `analyze_listening_habits` | Analyze listening patterns | `timeframe` (optional) |
| `explore_artist` | Deep dive into artist | `artist_name` (required) |

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
