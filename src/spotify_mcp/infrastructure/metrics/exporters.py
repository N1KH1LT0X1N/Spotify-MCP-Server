"""
Metrics exporters for Prometheus integration.

Provides HTTP endpoint for Prometheus scraping (optional).
"""

try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    generate_latest = None
    CONTENT_TYPE_LATEST = "text/plain"


def metrics_endpoint() -> tuple:
    """
    Generate Prometheus metrics endpoint response.

    Returns:
        Tuple of (content, content_type)

    Example:
        # In Flask:
        @app.route('/metrics')
        def metrics():
            content, content_type = metrics_endpoint()
            return Response(content, mimetype=content_type)

        # In FastAPI:
        @app.get("/metrics")
        async def metrics():
            content, content_type = metrics_endpoint()
            return Response(content=content, media_type=content_type)
    """
    if not PROMETHEUS_AVAILABLE:
        return (
            "# Metrics not available\n# Install prometheus-client: pip install prometheus-client\n",
            "text/plain"
        )

    return (generate_latest(), CONTENT_TYPE_LATEST)


def get_current_metrics() -> dict:
    """
    Get current metrics as a dictionary (for debugging).

    Returns:
        Dict with current metric values
    """
    if not PROMETHEUS_AVAILABLE:
        return {
            'error': 'Prometheus client not installed',
            'metrics_enabled': False
        }

    from .collectors import get_metrics_collector

    collector = get_metrics_collector()

    return {
        'metrics_enabled': collector.enabled,
        'server_version': '1.1.0',
        'note': 'Full metrics available at /metrics endpoint'
    }
