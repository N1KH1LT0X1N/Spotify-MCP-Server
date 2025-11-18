# Configuration Management

Centralized, type-safe configuration with environment variable support and validation.

## Overview

The configuration system provides:
- **Type Safety**: Pydantic models with automatic validation
- **Environment Variables**: Load config from `.env` files or environment
- **Validation**: Automatic validation of all configuration values
- **Singleton Pattern**: Cached settings for performance
- **IDE Support**: Full autocomplete and type hints

## Quick Start

```python
from spotify_mcp.config import get_settings

# Get settings (singleton - loaded once, cached)
settings = get_settings()

# Access configuration
print(settings.spotify.client_id)
print(settings.cache.backend)
print(settings.logging.level)
```

## Configuration Sections

### Spotify Configuration

Spotify API credentials and OAuth settings.

```python
settings.spotify.client_id      # Spotify Client ID
settings.spotify.client_secret  # Spotify Client Secret
settings.spotify.redirect_uri   # OAuth redirect URI
```

**Environment Variables:**
- `SPOTIFY_CLIENT_ID` - Spotify application client ID
- `SPOTIFY_CLIENT_SECRET` - Spotify application client secret
- `SPOTIFY_REDIRECT_URI` - OAuth callback URL (default: `http://127.0.0.1:8888/callback`)

### Cache Configuration

Cache backend and settings.

```python
settings.cache.backend          # "memory" or "redis"
settings.cache.redis_url        # Redis connection URL
settings.cache.max_memory_size  # Max entries in memory cache
```

**Environment Variables:**
- `CACHE_BACKEND` - Cache backend: `memory` or `redis` (default: `memory`)
- `REDIS_URL` - Redis URL (default: `redis://localhost:6379/0`)
- `CACHE_MAX_SIZE` - Maximum memory cache entries (default: `1000`)

### Metrics Configuration

Prometheus metrics collection settings.

```python
settings.metrics.enabled  # Enable metrics collection
settings.metrics.port     # Metrics HTTP server port
```

**Environment Variables:**
- `METRICS_ENABLED` - Enable metrics: `true` or `false` (default: `false`)
- `METRICS_PORT` - Metrics server port (default: `8000`)

### Logging Configuration

Structured logging settings.

```python
settings.logging.level   # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
settings.logging.format  # Log format ("human" or "json")
settings.logging.file    # Optional log file path
```

**Environment Variables:**
- `LOG_LEVEL` - Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (default: `INFO`)
- `LOG_FORMAT` - Format: `human` or `json` (default: `human`)
- `LOG_FILE` - Optional file path for logs

### General Settings

Application-level settings.

```python
settings.environment     # "development", "staging", "production"
settings.debug           # Debug mode boolean
settings.is_production   # Convenience property
settings.is_development  # Convenience property
```

**Environment Variables:**
- `ENVIRONMENT` - Environment: `development`, `staging`, `production` (default: `development`)
- `DEBUG` - Debug mode: `true` or `false` (default: `false`)

## Usage Examples

### Basic Usage

```python
from spotify_mcp.config import get_settings

settings = get_settings()

# Use in your code
if settings.cache.backend == "redis":
    cache = RedisCache(settings.cache.redis_url)
else:
    cache = MemoryCache(settings.cache.max_memory_size)
```

### Environment-Based Configuration

```python
settings = get_settings()

if settings.is_production:
    # Production-specific setup
    setup_monitoring()
    enable_security()
elif settings.is_development:
    # Development-specific setup
    enable_debug_logging()
```

### Logging Configuration

```python
from spotify_mcp.infrastructure.logging import setup_logging, LogLevel

settings = get_settings()

setup_logging(
    level=LogLevel[settings.logging.level],
    format_type=settings.logging.format,
    log_file=settings.logging.file
)
```

### Cache Configuration

```python
from spotify_mcp.infrastructure.cache import get_cache_manager

settings = get_settings()

cache_manager = get_cache_manager(
    backend=settings.cache.backend,
    redis_url=settings.cache.redis_url,
    max_memory_size=settings.cache.max_memory_size
)
```

## Environment Files

### Development (`.env.development`)

```bash
# Spotify
SPOTIFY_CLIENT_ID=your_dev_client_id
SPOTIFY_CLIENT_SECRET=your_dev_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback

# Cache
CACHE_BACKEND=memory
CACHE_MAX_SIZE=1000

# Metrics
METRICS_ENABLED=false

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=human

# General
ENVIRONMENT=development
DEBUG=true
```

### Production (`.env.production`)

```bash
# Spotify
SPOTIFY_CLIENT_ID=your_prod_client_id
SPOTIFY_CLIENT_SECRET=your_prod_client_secret
SPOTIFY_REDIRECT_URI=https://your-domain.com/callback

# Cache
CACHE_BACKEND=redis
REDIS_URL=redis://redis:6379/0
CACHE_MAX_SIZE=10000

# Metrics
METRICS_ENABLED=true
METRICS_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/spotify-mcp/app.log

# General
ENVIRONMENT=production
DEBUG=false
```

## Validation

All configuration values are automatically validated:

```python
# These will raise validation errors:
settings.cache.backend = "invalid"  # Must be "memory" or "redis"
settings.logging.level = "TRACE"    # Must be DEBUG, INFO, WARNING, ERROR, or CRITICAL
settings.metrics.port = 99999       # Must be 0-65535
```

## Type Safety

Full type hints and IDE support:

```python
from spotify_mcp.config import get_settings

settings = get_settings()

# IDE will autocomplete:
settings.spotify.        # -> client_id, client_secret, redirect_uri
settings.cache.          # -> backend, redis_url, max_memory_size
settings.logging.        # -> level, format, file
settings.metrics.        # -> enabled, port
```

## Testing

### Override Settings for Tests

```python
from spotify_mcp.config import Settings, SpotifyConfig

def test_with_custom_settings():
    # Create custom settings for testing
    test_settings = Settings(
        spotify=SpotifyConfig(
            client_id="test_id",
            client_secret="test_secret"
        )
    )

    # Use test settings
    assert test_settings.spotify.client_id == "test_id"
```

### Mock Environment Variables

```python
import os
from unittest.mock import patch

def test_env_loading():
    with patch.dict(os.environ, {
        "SPOTIFY_CLIENT_ID": "test_id",
        "LOG_LEVEL": "DEBUG",
        "CACHE_BACKEND": "redis"
    }):
        settings = Settings.from_env()
        assert settings.spotify.client_id == "test_id"
        assert settings.logging.level == "DEBUG"
        assert settings.cache.backend == "redis"
```

## Migration from Direct Environment Access

### Before

```python
import os

client_id = os.getenv("SPOTIFY_CLIENT_ID", "")
log_level = os.getenv("LOG_LEVEL", "INFO")
cache_backend = os.getenv("CACHE_BACKEND", "memory")

# No validation, no type safety
if cache_backend not in ["memory", "redis"]:
    raise ValueError("Invalid cache backend")
```

### After

```python
from spotify_mcp.config import get_settings

settings = get_settings()

# Validated, type-safe access
client_id = settings.spotify.client_id
log_level = settings.logging.level
cache_backend = settings.cache.backend  # Guaranteed to be valid
```

## Best Practices

### 1. Use Settings Singleton

```python
# Good - reuses cached settings
from spotify_mcp.config import get_settings

def function1():
    settings = get_settings()  # Loaded from env

def function2():
    settings = get_settings()  # Returns cached instance
```

### 2. Load Settings Early

```python
# In your main entry point
def main():
    settings = get_settings()  # Load and validate all config upfront

    # If there are config errors, fail fast
    if not settings.spotify.client_id:
        logger.error("SPOTIFY_CLIENT_ID not set")
        sys.exit(1)

    # Continue with application...
```

### 3. Environment-Specific Config

```python
settings = get_settings()

if settings.is_production:
    # Strict error handling in production
    raise_on_error = True
else:
    # More permissive in development
    raise_on_error = False
```

### 4. Never Hard-Code Sensitive Data

```python
# Bad
SPOTIFY_CLIENT_SECRET = "abc123"

# Good
settings = get_settings()
client_secret = settings.spotify.client_secret
```

## Troubleshooting

### Validation Errors

If you see validation errors:

```python
pydantic.ValidationError: 1 validation error for CacheConfig
backend
  backend must be 'memory' or 'redis' (type=value_error)
```

Check your environment variables:
```bash
echo $CACHE_BACKEND  # Should be "memory" or "redis"
```

### Missing Environment Variables

If required variables are missing:

```bash
# Check what's set
env | grep SPOTIFY

# Set missing variables
export SPOTIFY_CLIENT_ID=your_id
export SPOTIFY_CLIENT_SECRET=your_secret
```

### Cache Not Updating

Settings are cached (singleton pattern). If you need fresh settings:

```python
from spotify_mcp.config.settings import get_settings

# Clear the cache
get_settings.cache_clear()

# Load fresh settings
settings = get_settings()
```

## See Also

- [Logging Infrastructure](../infrastructure/logging/README.md) - Structured logging
- [Cache Infrastructure](../infrastructure/cache/README.md) - Intelligent caching
- [Metrics Infrastructure](../infrastructure/metrics/README.md) - Prometheus metrics
