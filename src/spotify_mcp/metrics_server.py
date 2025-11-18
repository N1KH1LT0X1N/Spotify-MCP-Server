#!/usr/bin/env python3
"""
Standalone HTTP server for Prometheus metrics.

This server runs alongside the main MCP server to expose metrics at /metrics endpoint.
The metrics are collected from the shared MetricsCollector singleton.

Usage:
    python -m spotify_mcp.metrics_server

The server will listen on port 8000 by default.
Set METRICS_PORT environment variable to change the port.
"""

import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

# Check if prometheus-client is available
try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("Warning: prometheus-client not installed. Install with: pip install prometheus-client")
    sys.exit(1)

# Import metrics collector to ensure singleton is initialized
from spotify_mcp.infrastructure.metrics import get_metrics_collector


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for Prometheus metrics endpoint."""

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-Type', CONTENT_TYPE_LATEST)
            self.end_headers()

            # Generate and send metrics
            metrics_output = generate_latest()
            self.wfile.write(metrics_output)

        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')

        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found. Try /metrics or /health')

    def log_message(self, format, *args):
        """Custom log format."""
        sys.stdout.write(f"[MetricsServer] {self.address_string()} - {format % args}\n")


def run_server(port: int = 8000):
    """
    Run the metrics HTTP server.

    Args:
        port: Port to listen on (default: 8000)
    """
    # Initialize metrics collector
    collector = get_metrics_collector()

    if not collector.enabled:
        print("Error: Prometheus metrics are not enabled")
        print("Install prometheus-client: pip install prometheus-client")
        sys.exit(1)

    server_address = ('', port)
    httpd = HTTPServer(server_address, MetricsHandler)

    print(f"Spotify MCP Metrics Server running on http://0.0.0.0:{port}")
    print(f"Metrics endpoint: http://0.0.0.0:{port}/metrics")
    print(f"Health endpoint: http://0.0.0.0:{port}/health")
    print("Press Ctrl+C to stop")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down metrics server...")
        httpd.shutdown()


def main():
    """Main entry point."""
    # Get port from environment or use default
    port = int(os.environ.get('METRICS_PORT', 8000))
    run_server(port)


if __name__ == '__main__':
    main()
