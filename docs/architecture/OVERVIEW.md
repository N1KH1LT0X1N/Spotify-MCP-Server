# 🏗️ Architecture Overview

## System Design

```
┌─────────────────────────────────────────────────────────────┐
│                      Claude Desktop                          │
│                    (or other MCP client)                     │
└─────────────────────────┬───────────────────────────────────┘
                          │ MCP Protocol (stdio)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Spotify MCP Server                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   server.py │  │   prompts   │  │     resources       │  │
│  │  (75 tools) │  │ (8 prompts) │  │   (8 resources)     │  │
│  └──────┬──────┘  └─────────────┘  └─────────────────────┘  │
│         │                                                    │
│  ┌──────▼──────────────────────────────────────────────┐    │
│  │              SpotifyClient (spotify_client.py)       │    │
│  │   • Error handling with retries                      │    │
│  │   • Rate limiting protection                         │    │
│  │   • Response caching                                 │    │
│  └──────┬───────────────────────────────────────────────┘    │
│         │                                                    │
│  ┌──────▼──────────────────────────────────────────────┐    │
│  │                 Infrastructure Layer                  │    │
│  │   • Cache (memory/redis)                             │    │
│  │   • Logging (structured JSON)                        │    │
│  │   • Metrics (Prometheus)                             │    │
│  └──────────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTPS
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     Spotify Web API                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. MCP Server (`server.py`)

- Entry point for all MCP communication
- Routes tool calls to appropriate handlers
- Manages resources and prompts
- Handles authentication state

### 2. Spotify Client (`spotify_client.py`)

- Wraps spotipy library
- Adds caching layer (10-100x performance)
- Implements retry logic with exponential backoff
- Sanitizes inputs for security

### 3. Tools (`tools/` directory)

75 tools organized by category:
- `playback.py` - Playback control
- `search.py` - Search functionality
- `library.py` - Library management
- `playlists.py` - Playlist operations
- `albums.py`, `artists.py`, `tracks.py` - Content
- `user.py` - User profile operations
- `composite.py` - Multi-step operations

### 4. Infrastructure

- **Cache**: Memory (default) or Redis for distributed
- **Logging**: Structured JSON with correlation IDs
- **Metrics**: Prometheus-compatible endpoints
- **CLI**: Rich terminal interface

---

## Design Decisions

### No Database Required

The server is stateless by design:
- Spotify is the source of truth for all data
- Tokens stored in environment variables
- Cache is in-memory (optional Redis for distribution)

### Caching Strategy

| Data Type | TTL | Reason |
|-----------|-----|--------|
| Track/Album/Artist metadata | 24h | Rarely changes |
| User library | 3-5 min | Occasional updates |
| Playback state | 10-30s | Changes frequently |

### Error Handling

1. Automatic retry with exponential backoff
2. Clear error messages for common issues
3. Graceful degradation when possible
4. Rate limit detection and waiting

---

## Security

- OAuth 2.0 PKCE flow for authentication
- Tokens never logged or exposed
- Input sanitization on all API calls
- Optional keyring integration for secure storage

See [SECURITY.md](../SECURITY.md) for full details.

---

## Scalability

For high-traffic scenarios:

1. **Redis Cache** - Shared cache across instances
2. **Extended Quota** - Apply to Spotify for higher limits
3. **Metrics** - Monitor with Prometheus/Grafana
4. **Load Balancing** - Stateless design allows horizontal scaling
