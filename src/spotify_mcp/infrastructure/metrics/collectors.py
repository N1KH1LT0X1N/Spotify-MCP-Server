"""
Metrics collectors for Spotify MCP Server.

Provides optional Prometheus metrics integration. Works without prometheus-client
installed, gracefully degrading to no-op implementations.
"""

import time
from typing import Optional, Dict, Any
from functools import wraps

# Try to import Prometheus, but make it optional
try:
    from prometheus_client import Counter, Histogram, Gauge, Info
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Create no-op classes
    class Counter:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
        def inc(self, *args, **kwargs):
            pass

    class Histogram:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
        def observe(self, *args, **kwargs):
            pass

    class Gauge:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
        def set(self, *args, **kwargs):
            pass
        def inc(self, *args, **kwargs):
            pass
        def dec(self, *args, **kwargs):
            pass

    class Info:
        def __init__(self, *args, **kwargs):
            pass
        def info(self, *args, **kwargs):
            pass


class MetricsCollector:
    """
    Centralized metrics collector for Spotify MCP Server.

    Gracefully handles missing prometheus-client package.
    """

    def __init__(self):
        self.enabled = PROMETHEUS_AVAILABLE

        # Tool call metrics
        self.tool_calls_total = Counter(
            'spotify_mcp_tool_calls_total',
            'Total number of tool calls',
            ['tool_name', 'status']
        )

        self.tool_call_duration = Histogram(
            'spotify_mcp_tool_call_duration_seconds',
            'Tool call duration in seconds',
            ['tool_name'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )

        # Cache metrics
        self.cache_operations_total = Counter(
            'spotify_mcp_cache_operations_total',
            'Total cache operations',
            ['operation', 'result']
        )

        self.cache_hit_rate = Gauge(
            'spotify_mcp_cache_hit_rate',
            'Current cache hit rate (0-100)',
            ['cache_type']
        )

        self.cache_size = Gauge(
            'spotify_mcp_cache_size',
            'Number of entries in cache',
            ['cache_type']
        )

        # Spotify API metrics
        self.spotify_api_calls_total = Counter(
            'spotify_mcp_spotify_api_calls_total',
            'Total Spotify API calls',
            ['method', 'status']
        )

        self.spotify_api_errors_total = Counter(
            'spotify_mcp_spotify_api_errors_total',
            'Total Spotify API errors',
            ['error_type', 'http_status']
        )

        # System metrics
        self.active_requests = Gauge(
            'spotify_mcp_active_requests',
            'Number of currently active requests'
        )

        # Server info
        self.server_info = Info(
            'spotify_mcp_server_info',
            'Server information'
        )

        # Set server info
        self.server_info.info({
            'version': '1.1.0',
            'python_version': self._get_python_version(),
            'metrics_enabled': str(self.enabled),
        })

    def _get_python_version(self) -> str:
        """Get Python version string."""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    def record_tool_call(self, tool_name: str, duration: float, status: str = 'success'):
        """Record a tool call."""
        if not self.enabled:
            return

        self.tool_calls_total.labels(tool_name=tool_name, status=status).inc()
        self.tool_call_duration.labels(tool_name=tool_name).observe(duration)

    def record_cache_operation(self, operation: str, result: str):
        """Record a cache operation (hit/miss)."""
        if not self.enabled:
            return

        self.cache_operations_total.labels(operation=operation, result=result).inc()

    def update_cache_stats(self, cache_type: str, hit_rate: float, size: int):
        """Update cache statistics."""
        if not self.enabled:
            return

        self.cache_hit_rate.labels(cache_type=cache_type).set(hit_rate)
        self.cache_size.labels(cache_type=cache_type).set(size)

    def record_spotify_api_call(self, method: str, status: str = 'success'):
        """Record a Spotify API call."""
        if not self.enabled:
            return

        self.spotify_api_calls_total.labels(method=method, status=status).inc()

    def record_spotify_api_error(self, error_type: str, http_status: int):
        """Record a Spotify API error."""
        if not self.enabled:
            return

        self.spotify_api_errors_total.labels(
            error_type=error_type,
            http_status=str(http_status)
        ).inc()

    def increment_active_requests(self):
        """Increment active requests counter."""
        if not self.enabled:
            return
        self.active_requests.inc()

    def decrement_active_requests(self):
        """Decrement active requests counter."""
        if not self.enabled:
            return
        self.active_requests.dec()


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """
    Get global metrics collector instance (singleton).

    Returns:
        Global metrics collector
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def track_tool_call(tool_name: str):
    """
    Decorator to track tool call metrics.

    Usage:
        @track_tool_call('play')
        def play(client, uri: str):
            return client.start_playback(uris=[uri])
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            collector = get_metrics_collector()
            collector.increment_active_requests()

            start_time = time.time()
            status = 'success'

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                duration = time.time() - start_time
                collector.record_tool_call(tool_name, duration, status)
                collector.decrement_active_requests()

        return wrapper
    return decorator


def track_cache_operation(operation: str, result: str):
    """
    Helper to track cache operations.

    Args:
        operation: 'get', 'set', 'delete'
        result: 'hit', 'miss', 'success'
    """
    collector = get_metrics_collector()
    collector.record_cache_operation(operation, result)


def update_cache_metrics(cache_type: str, stats: Dict[str, Any]):
    """
    Update cache metrics from stats dictionary.

    Args:
        cache_type: 'memory' or 'redis'
        stats: Stats dict from cache.get_stats()
    """
    collector = get_metrics_collector()

    # Parse hit rate (remove % sign if present)
    hit_rate_str = stats.get('hit_rate', '0%')
    hit_rate = float(hit_rate_str.rstrip('%'))

    size = stats.get('size', 0)

    collector.update_cache_stats(cache_type, hit_rate, size)
