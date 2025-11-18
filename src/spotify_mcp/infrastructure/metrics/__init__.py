"""Metrics infrastructure for Spotify MCP Server."""

from .collectors import (
    get_metrics_collector,
    track_tool_call,
    track_cache_operation,
    update_cache_metrics,
    MetricsCollector,
)

try:
    from .exporters import metrics_endpoint
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    metrics_endpoint = None

__all__ = [
    'get_metrics_collector',
    'track_tool_call',
    'track_cache_operation',
    'update_cache_metrics',
    'MetricsCollector',
    'metrics_endpoint',
    'METRICS_AVAILABLE',
]
