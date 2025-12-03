# 🏢 Enterprise Features

Optional features for production deployments.

---

## Metrics & Monitoring

### Enable Prometheus Metrics

```bash
pip install prometheus-client
```

```bash
# Environment
ENABLE_METRICS=true
METRICS_PORT=9090
```

Access metrics at: `http://localhost:9090/metrics`

### Docker Compose Stack

```bash
docker-compose up -d
# Includes: spotify-mcp, redis, prometheus, grafana
```

---

## CLI Tool

```bash
pip install -e ".[cli]"
spotify-mcp-cli
```

Commands:
- `playback` - Control playback
- `search` - Search Spotify
- `playlist` - Manage playlists
- `library` - View library
- `device` - Manage devices
- `status` - Current status

---

## Redis Caching

For distributed caching across multiple instances:

```bash
pip install redis
```

```bash
SPOTIFY_CACHE_BACKEND=redis
REDIS_URL=redis://localhost:6379
```

---

## Secure Token Storage

Use OS keyring instead of .env file:

```bash
pip install keyring
python scripts/enterprise_cli.py enable-keychain
```

---

## Structured Logging

Enable JSON logging for log aggregation:

```bash
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## Quick Checklist

| Feature | Install | Environment |
|---------|---------|-------------|
| Metrics | `pip install prometheus-client` | `ENABLE_METRICS=true` |
| CLI | `pip install -e ".[cli]"` | - |
| Redis | `pip install redis` | `REDIS_URL=...` |
| Keyring | `pip install keyring` | Run enable script |
| Logging | - | `LOG_FORMAT=json` |

All features are optional and backward-compatible.
