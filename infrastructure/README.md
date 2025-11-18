# Infrastructure

This directory contains infrastructure configuration for production deployments.

## Prometheus

Prometheus configuration for metrics collection.

### Files
- `prometheus/prometheus.yml` - Prometheus server configuration

### Usage

Start with monitoring profile:
```bash
docker-compose --profile monitoring up
```

Access Prometheus at: http://localhost:9090

### Metrics Endpoint

The Spotify MCP Server exposes metrics at `/metrics` on port 8000. This endpoint is automatically scraped by Prometheus every 10 seconds.

## Grafana

Grafana dashboards for metrics visualization.

### Files
- `grafana/provisioning/datasources/prometheus.yml` - Auto-configured Prometheus datasource
- `grafana/provisioning/dashboards/dashboard.yml` - Dashboard provisioning config

### Usage

Grafana is included in the monitoring profile:
```bash
docker-compose --profile monitoring up
```

Access Grafana at: http://localhost:3000
- Username: `admin`
- Password: `admin`

The Prometheus datasource is pre-configured and ready to use.

### Creating Dashboards

Key metrics to monitor:

1. **Request Rate**
   ```promql
   rate(spotify_mcp_tool_calls_total[5m])
   ```

2. **Error Rate**
   ```promql
   rate(spotify_mcp_tool_calls_total{status="error"}[5m])
   ```

3. **P95 Latency**
   ```promql
   histogram_quantile(0.95, rate(spotify_mcp_tool_call_duration_seconds_bucket[5m]))
   ```

4. **Cache Hit Rate**
   ```promql
   spotify_mcp_cache_hit_rate
   ```

5. **Active Requests**
   ```promql
   spotify_mcp_active_requests
   ```

## Architecture

```
┌─────────────────┐
│ Spotify MCP     │
│ Server          │
│ :8000/metrics   │
└────────┬────────┘
         │
         │ scrape
         ▼
┌─────────────────┐
│ Prometheus      │
│ :9090           │
└────────┬────────┘
         │
         │ query
         ▼
┌─────────────────┐
│ Grafana         │
│ :3000           │
└─────────────────┘
```

## Production Considerations

1. **Retention**: Configure Prometheus retention based on your needs
2. **Storage**: Use persistent volumes for both Prometheus and Grafana
3. **Security**: Change default Grafana credentials
4. **Alerts**: Configure alerting rules in `prometheus/alerts.yml`
5. **Backups**: Regularly backup Grafana dashboards and Prometheus data
