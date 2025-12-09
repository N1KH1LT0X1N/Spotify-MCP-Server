# 🚀 Deployment Guide

## Deployment Options

### Option 1: Local Development (Recommended for Personal Use)

Run directly on your machine with Claude Desktop.

```bash
# 1. Install in development mode
pip install -e .

# 2. One-time authentication (opens browser)
python -m spotify_mcp.auth

# 3. Verify server starts (optional)
python -m spotify_mcp.spotify_server
# Press Ctrl+C to stop after seeing "✓ Spotify MCP Server v3.0 Enhanced initialized"

# 4. Add to Claude Desktop config (see below)
# 5. Restart Claude Desktop

# Alternative: Use installed command
spotify-mcp
```

**Pros:** Simple setup, no infrastructure needed, automatic token refresh  
**Cons:** Only works on your machine, requires Claude Desktop restart after config changes

**System Requirements:**
- Python 3.10+
- 50MB disk space
- Internet connection for Spotify API
- Spotify Premium (for playback control)

---

### Option 2: Docker (Recommended for Sharing)

Run in a container for consistent environment.

```bash
# Build
docker build -t spotify-mcp .

# Run with env file
docker run --env-file .env spotify-mcp
```

**Pros:** Portable, consistent environment  
**Cons:** Requires Docker

---

### Option 3: Docker Compose (Production)

Full stack with monitoring.

```bash
# Start all services
docker-compose up -d

# Services:
# - spotify-mcp: Main server
# - redis: Cache backend (optional)
# - prometheus: Metrics collection
# - grafana: Dashboards
```

**Pros:** Full observability, production-ready  
**Cons:** More complex, resource-intensive

---

## Pre-Deployment Checklist

### ✅ Required

- [ ] Spotify Developer account created
- [ ] App registered in Spotify Dashboard
- [ ] Client ID and Secret obtained
- [ ] Redirect URI set to `http://127.0.0.1:8888/callback`
- [ ] `.env` file configured with credentials
- [ ] Initial authentication completed (`python -m spotify_mcp.auth`)
- [ ] Tokens saved to `.env` file

### ✅ Recommended

- [ ] Tested with `python tools/verify_tools.py`
- [ ] Claude Desktop config tested
- [ ] Spotify Premium for playback control

### ⚠️ Optional (Enterprise)

- [ ] Redis installed for distributed caching
- [ ] Prometheus + Grafana for monitoring
- [ ] Keyring configured for secure token storage

---

## Environment Variables

### Required

```bash
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

### After Authentication

```bash
SPOTIFY_ACCESS_TOKEN=BQD...
SPOTIFY_REFRESH_TOKEN=AQD...
```

### Optional

```bash
# Cache
SPOTIFY_CACHE_BACKEND=memory  # or "redis"
REDIS_URL=redis://localhost:6379

# Metrics
ENABLE_METRICS=true
METRICS_PORT=9090

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## Claude Desktop Configuration

### Windows

Location: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "spotify": {
      "command": "python",
      "args": ["-m", "spotify_mcp.server"],
      "env": {
        "SPOTIFY_CLIENT_ID": "your_id",
        "SPOTIFY_CLIENT_SECRET": "your_secret",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback",
        "PYTHONPATH": "C:\\path\\to\\spotify_mcp\\src"
      }
    }
  }
}
```

### macOS

Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "spotify": {
      "command": "python",
      "args": ["-m", "spotify_mcp.server"],
      "env": {
        "SPOTIFY_CLIENT_ID": "your_id",
        "SPOTIFY_CLIENT_SECRET": "your_secret",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback",
        "PYTHONPATH": "/path/to/spotify_mcp/src"
      }
    }
  }
}
```

---

## Verification

### Test Installation

```bash
# Check tools are loading
cd src && python -c "from spotify_mcp.server import TOOL_FUNCTIONS; print(len(TOOL_FUNCTIONS))"
# Expected: 75

# Full verification
python tools/verify_tools.py
```

### Test with Claude

1. Restart Claude Desktop after config change
2. Look for Spotify hammer icon in Claude
3. Ask: "What Spotify tools do you have?"
4. Ask: "Search for Taylor Swift songs"

---

## Troubleshooting Deployment

### "ModuleNotFoundError: spotify_mcp"

Set PYTHONPATH to the `src` directory:
```json
"PYTHONPATH": "C:\\full\\path\\to\\spotify_mcp\\src"
```

### "No Spotify tokens found"

Run authentication first:
```bash
python -m spotify_mcp.auth
```

### "Invalid redirect URI"

Use `127.0.0.1` not `localhost`:
```
http://127.0.0.1:8888/callback
```

### Claude doesn't show Spotify

1. Check Claude Desktop logs for errors
2. Verify config JSON syntax
3. Restart Claude Desktop completely

---

## Going to Production

For production use, consider:

1. **Extended Quota Mode** - Apply to Spotify for higher rate limits
2. **Redis Caching** - For multi-instance deployments  
3. **Prometheus Metrics** - For monitoring and alerting
4. **Secure Token Storage** - Use keyring instead of .env
5. **HTTPS** - If exposing callback endpoint publicly

See [Enterprise Features](enterprise/quickstart.md) for details.
