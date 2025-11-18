# Structured Logging Infrastructure

Production-grade structured logging with JSON formatting, correlation IDs, and contextual information for debugging and monitoring.

## Features

- **JSON Formatting**: Structured logs for production environments
- **Human-Readable**: Colored, easy-to-read logs for development
- **Correlation IDs**: Automatic request tracing with UUIDs
- **Context Management**: Add contextual information to all logs
- **Thread-Safe**: Works correctly in multi-threaded environments
- **Exception Tracking**: Automatic exception formatting
- **Configurable**: Multiple log levels and output formats

## Quick Start

### Basic Usage

```python
from spotify_mcp.infrastructure.logging import get_logger, setup_logging, LogLevel

# Setup logging (do this once at application startup)
setup_logging(level=LogLevel.INFO, format_type="human")

# Get a logger
logger = get_logger(__name__)

# Log messages
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### Human-Readable Format (Development)

```python
setup_logging(level=LogLevel.DEBUG, format_type="human")
```

Output:
```
INFO     12:34:56.789 [a1b2c3d4] spotify_mcp.server Starting application
DEBUG    12:34:56.790 [a1b2c3d4] spotify_mcp.cache Cache hit (user_id=123)
ERROR    12:34:56.791 [a1b2c3d4] spotify_mcp.api API call failed
```

### JSON Format (Production)

```python
setup_logging(level=LogLevel.INFO, format_type="json")
```

Output:
```json
{
  "timestamp": "2024-11-18T20:34:56.789Z",
  "level": "INFO",
  "logger": "spotify_mcp.server",
  "message": "Starting application",
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "source": {
    "file": "server.py",
    "line": 42,
    "function": "main"
  }
}
```

## Correlation IDs

Every log message automatically includes a correlation ID that persists across all logs in the same thread. This makes it easy to trace requests through the system.

```python
from spotify_mcp.infrastructure.logging import get_logger, set_correlation_id

logger = get_logger(__name__)

# Set a custom correlation ID (e.g., from incoming request)
set_correlation_id("request-123")

logger.info("Processing request")
logger.info("Request completed")
# Both logs will have correlation_id: "request-123"
```

## Context Management

Add contextual information that will be included in all subsequent logs:

```python
from spotify_mcp.infrastructure.logging import get_logger, add_log_context, log_context

logger = get_logger(__name__)

# Add context permanently (for this thread)
add_log_context(user_id="user123", session="abc")
logger.info("User logged in")  # Includes user_id and session

# Add context temporarily with context manager
with log_context(operation="playlist_create"):
    logger.info("Creating playlist")  # Includes all context
    logger.info("Playlist created")
# Outside context manager, operation is no longer included
```

### JSON Output with Context

```json
{
  "timestamp": "2024-11-18T20:34:56.789Z",
  "level": "INFO",
  "logger": "spotify_mcp.tools",
  "message": "Creating playlist",
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "context": {
    "user_id": "user123",
    "session": "abc",
    "operation": "playlist_create"
  },
  "source": {
    "file": "playlists.py",
    "line": 156,
    "function": "create_playlist"
  }
}
```

## Exception Logging

Exceptions are automatically formatted and included in logs:

```python
logger = get_logger(__name__)

try:
    raise ValueError("Something went wrong")
except Exception as e:
    logger.error("Failed to process request", exc_info=True)
```

JSON output includes full exception traceback:
```json
{
  "level": "ERROR",
  "message": "Failed to process request",
  "exception": "Traceback (most recent call last):\n  File ...",
  ...
}
```

## Configuration

### Log Levels

```python
from spotify_mcp.infrastructure.logging import LogLevel

# Available levels
LogLevel.DEBUG      # Detailed diagnostic information
LogLevel.INFO       # General informational messages
LogLevel.WARNING    # Warning messages
LogLevel.ERROR      # Error messages
LogLevel.CRITICAL   # Critical errors
```

### File Logging

Write logs to a file (always in JSON format):

```python
from pathlib import Path

setup_logging(
    level=LogLevel.INFO,
    format_type="human",  # Console output
    log_file=Path("/var/log/spotify-mcp/app.log")
)
```

### Environment-Based Configuration

```python
import os
from spotify_mcp.infrastructure.logging import setup_logging, LogLevel

# Use environment variables for configuration
log_level = os.getenv("LOG_LEVEL", "INFO")
log_format = os.getenv("LOG_FORMAT", "human")  # "human" or "json"

setup_logging(
    level=LogLevel[log_level],
    format_type=log_format
)
```

## Integration Examples

### MCP Server Integration

```python
from spotify_mcp.infrastructure.logging import get_logger, log_context

logger = get_logger(__name__)

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    with log_context(tool=name):
        logger.info("Tool called", extra={"arguments": arguments})

        try:
            result = execute_tool(name, arguments)
            logger.info("Tool completed successfully")
            return result
        except Exception as e:
            logger.error("Tool failed", exc_info=True)
            raise
```

### Spotify Client Integration

```python
from spotify_mcp.infrastructure.logging import get_logger, add_log_context

logger = get_logger(__name__)

class SpotifyClient:
    def __init__(self, sp):
        self.sp = sp
        add_log_context(client="spotify")

    def play(self, **kwargs):
        logger.debug("Starting playback", extra={"kwargs": kwargs})

        try:
            result = self.sp.start_playback(**kwargs)
            logger.info("Playback started successfully")
            return result
        except SpotifyException as e:
            logger.error("Playback failed", exc_info=True)
            raise
```

### Cache Integration

```python
from spotify_mcp.infrastructure.logging import get_logger

logger = get_logger(__name__)

def get(self, key: str):
    value = self._cache.get(key)

    if value is None:
        logger.debug("Cache miss", extra={"key": key})
        self._misses += 1
    else:
        logger.debug("Cache hit", extra={"key": key})
        self._hits += 1

    return value
```

## Best Practices

### 1. Use Appropriate Log Levels

- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: General informational messages about application progress
- **WARNING**: Something unexpected happened but the application continues
- **ERROR**: An error occurred, functionality may be impaired
- **CRITICAL**: A serious error, the application may not be able to continue

### 2. Include Context

```python
# Bad
logger.info("Request completed")

# Good
logger.info("Request completed", extra={"duration_ms": 123, "status": 200})
```

### 3. Use Structured Data

```python
# Bad
logger.info(f"User {user_id} created playlist {playlist_id}")

# Good
with log_context(user_id=user_id, playlist_id=playlist_id):
    logger.info("Playlist created")
```

### 4. Don't Log Sensitive Information

```python
# Bad - logs credentials
logger.info("Auth token: " + token)

# Good - logs sanitized info
logger.info("User authenticated", extra={"user_id": user_id})
```

### 5. Use Exceptions Wisely

```python
# Bad - loses exception context
except Exception as e:
    logger.error(str(e))

# Good - includes full traceback
except Exception as e:
    logger.error("Operation failed", exc_info=True)
```

## Monitoring and Alerts

### Querying JSON Logs

With structured JSON logs, you can easily query and analyze logs:

```bash
# Find all errors in the last hour
cat app.log | jq 'select(.level == "ERROR")'

# Count errors by logger
cat app.log | jq -r 'select(.level == "ERROR") | .logger' | sort | uniq -c

# Find all logs for a specific correlation ID
cat app.log | jq 'select(.correlation_id == "abc123")'

# Find slow operations
cat app.log | jq 'select(.context.duration_ms > 1000)'
```

### Integration with Log Aggregation

JSON logs work seamlessly with log aggregation tools:

- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Splunk**: Parse JSON automatically
- **Datadog**: Native JSON support
- **CloudWatch Logs**: JSON insights

### Setting Up Alerts

Example alert rules based on structured logs:

```
# Alert on high error rate
COUNT(level == "ERROR") > 10 IN 5 MINUTES

# Alert on critical errors
level == "CRITICAL"

# Alert on slow operations
context.duration_ms > 5000
```

## Performance Considerations

- **Logging Overhead**: Minimal (<1ms per log statement)
- **JSON Formatting**: Slightly slower than plain text, but negligible in production
- **File I/O**: Asynchronous handlers recommended for high-volume logging
- **Third-Party Loggers**: Automatically suppressed to reduce noise

## Migration from Print Statements

Replace existing print statements:

```python
# Before
print("Starting application")
print(f"Processing {len(items)} items")

# After
logger = get_logger(__name__)
logger.info("Starting application")
logger.info("Processing items", extra={"count": len(items)})
```

## Testing

When testing, you can verify log output:

```python
import logging
from spotify_mcp.infrastructure.logging import get_logger, setup_logging

def test_logging():
    setup_logging(level=LogLevel.DEBUG, format_type="human")
    logger = get_logger("test")

    with log_context(test_id="123"):
        logger.info("Test message")
        # Verify log output contains correlation_id and test_id
```

## Troubleshooting

### Logs Not Appearing

```python
# Ensure logging is set up
from spotify_mcp.infrastructure.logging import setup_logging, LogLevel

setup_logging(level=LogLevel.DEBUG, format_type="human")
```

### Wrong Log Level

```python
# Check current log level
import logging
print(logging.getLogger().level)  # Should be 10 (DEBUG), 20 (INFO), etc.
```

### Context Not Included

Make sure you're adding context in the same thread:

```python
# This won't work (different threads)
thread = Thread(target=lambda: add_log_context(user="abc"))
thread.start()
logger.info("Message")  # Won't have user context

# This works (same thread)
add_log_context(user="abc")
logger.info("Message")  # Will have user context
```

## See Also

- [Metrics Infrastructure](../metrics/README.md) - Prometheus metrics collection
- [Cache Infrastructure](../cache/README.md) - Intelligent caching layer
- [Main Documentation](../../../docs/README.md) - Complete project documentation
