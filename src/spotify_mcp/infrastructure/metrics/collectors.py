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

        # Rate limit metrics (Phase 3.1)
        self.rate_limit_remaining = Gauge(
            'spotify_mcp_rate_limit_remaining',
            'Spotify API rate limit remaining requests',
            ['tier']  # per_second, per_minute, per_hour
        )

        self.rate_limit_wait_time = Histogram(
            'spotify_mcp_rate_limit_wait_seconds',
            'Time spent waiting for rate limit',
            buckets=[0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )

        # Circuit breaker metrics (Phase 3.1)
        self.circuit_breaker_state = Gauge(
            'spotify_mcp_circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 2=half_open)',
            ['name', 'state']
        )

        self.circuit_breaker_failures = Counter(
            'spotify_mcp_circuit_breaker_failures_total',
            'Total circuit breaker failures',
            ['name']
        )

        self.circuit_breaker_successes = Counter(
            'spotify_mcp_circuit_breaker_successes_total',
            'Total circuit breaker successes',
            ['name']
        )

        # Cache enhancement metrics (Phase 3.1)
        self.cache_invalidations = Counter(
            'spotify_mcp_cache_invalidations_total',
            'Total cache invalidations',
            ['resource_type']
        )

        self.cache_memory_bytes = Gauge(
            'spotify_mcp_cache_memory_bytes',
            'Approximate cache memory usage in bytes',
            ['cache_type']
        )

        # Health check metrics (Phase 3.1)
        self.health_check_status = Gauge(
            'spotify_mcp_health_check',
            'Health check status (1=healthy, 0=unhealthy)',
            ['check', 'status']
        )

        self.health_check_duration = Histogram(
            'spotify_mcp_health_check_duration_seconds',
            'Health check execution duration',
            ['check'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
        )

        # Per-endpoint latency (Phase 3.1)
        self.spotify_endpoint_latency = Histogram(
            'spotify_mcp_spotify_endpoint_duration_seconds',
            'Spotify API endpoint latency',
            ['endpoint', 'method'],
            buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0]
        )

        # Tool request metrics by category
        self.tool_requests_total = Counter(
            'spotify_mcp_tool_requests_total',
            'Total tool requests by category',
            ['category', 'tool', 'status']
        )

        # Server info
        self.server_info = Info(
            'spotify_mcp_server_info',
            'Server information'
        )

        # Set server info
        self.server_info.info({
            'version': '1.3.0',  # Updated version
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

    # Phase 3.1: Enhanced metrics methods

    def update_rate_limit(self, tier: str, remaining: int):
        """
        Update rate limit remaining count.

        Args:
            tier: 'per_second', 'per_minute', or 'per_hour'
            remaining: Number of requests remaining
        """
        if not self.enabled:
            return
        self.rate_limit_remaining.labels(tier=tier).set(remaining)

    def record_rate_limit_wait(self, wait_time: float):
        """Record time spent waiting for rate limit."""
        if not self.enabled:
            return
        self.rate_limit_wait_time.observe(wait_time)

    def update_circuit_breaker_state(self, name: str, state: str):
        """
        Update circuit breaker state metric.

        Args:
            name: Circuit breaker name
            state: 'closed', 'open', or 'half_open'
        """
        if not self.enabled:
            return

        # Reset all states for this circuit breaker
        for s in ['closed', 'open', 'half_open']:
            self.circuit_breaker_state.labels(name=name, state=s).set(0)

        # Set the current state to 1
        self.circuit_breaker_state.labels(name=name, state=state).set(1)

    def record_circuit_breaker_failure(self, name: str):
        """Record circuit breaker failure."""
        if not self.enabled:
            return
        self.circuit_breaker_failures.labels(name=name).inc()

    def record_circuit_breaker_success(self, name: str):
        """Record circuit breaker success."""
        if not self.enabled:
            return
        self.circuit_breaker_successes.labels(name=name).inc()

    def record_cache_invalidation(self, resource_type: str):
        """Record cache invalidation."""
        if not self.enabled:
            return
        self.cache_invalidations.labels(resource_type=resource_type).inc()

    def update_cache_memory_usage(self, cache_type: str, bytes_used: int):
        """Update cache memory usage."""
        if not self.enabled:
            return
        self.cache_memory_bytes.labels(cache_type=cache_type).set(bytes_used)

    def record_health_check(self, check_name: str, healthy: bool, duration: float):
        """
        Record health check result.

        Args:
            check_name: Name of the health check
            healthy: Whether the check passed
            duration: Time taken to execute check
        """
        if not self.enabled:
            return

        status = 'healthy' if healthy else 'unhealthy'

        # Reset both statuses
        self.health_check_status.labels(check=check_name, status='healthy').set(0)
        self.health_check_status.labels(check=check_name, status='unhealthy').set(0)

        # Set the current status
        self.health_check_status.labels(check=check_name, status=status).set(1)

        # Record duration
        self.health_check_duration.labels(check=check_name).observe(duration)

    def record_spotify_endpoint_latency(self, endpoint: str, method: str, duration: float):
        """
        Record Spotify API endpoint latency.

        Args:
            endpoint: API endpoint path (e.g., '/v1/me/player/play')
            method: HTTP method ('GET', 'POST', 'PUT', 'DELETE')
            duration: Request duration in seconds
        """
        if not self.enabled:
            return
        self.spotify_endpoint_latency.labels(endpoint=endpoint, method=method).observe(duration)

    def record_tool_request(self, category: str, tool_name: str, status: str):
        """
        Record tool request by category.

        Args:
            category: Tool category (playback, library, search, etc.)
            tool_name: Name of the tool
            status: 'success' or 'error'
        """
        if not self.enabled:
            return
        self.tool_requests_total.labels(category=category, tool=tool_name, status=status).inc()


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
