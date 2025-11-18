#!/bin/bash
# Entrypoint script for Spotify MCP Server with metrics

set -e

# Start metrics server in background if prometheus-client is installed
if python -c "import prometheus_client" 2>/dev/null; then
    echo "Starting Prometheus metrics server on port 8000..."
    python -m spotify_mcp.metrics_server &
    METRICS_PID=$!

    # Give metrics server time to start
    sleep 2
fi

# Start the main MCP server
echo "Starting Spotify MCP Server..."
exec python -m spotify_mcp.server

# Cleanup on exit
trap "kill $METRICS_PID 2>/dev/null || true" EXIT
