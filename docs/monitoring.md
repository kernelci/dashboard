# Monitoring and Metrics

This document explains how to use the monitoring system in the KernelCI Dashboard project.

## Quick Start

### 1. Start Monitoring Services
```bash
docker compose -f docker-compose.monitoring.yml up -d
```

### 2. Start Your Backend

#### Option A: Using Docker Compose (Recommended)
```bash
# Add monitoring configuration to .env.backend
echo "PROMETHEUS_METRICS_ENABLED=true" >> .env.backend
echo "PROMETHEUS_METRICS_PORT=8001" >> .env.backend
echo "PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc_dir" >> .env.backend

# Start the backend with monitoring enabled
docker compose up -d backend

# The backend will automatically expose port 8001 for metrics when PROMETHEUS_METRICS_ENABLED=true
```

> **Note**: For detailed backend setup instructions, see [backend/README.md](../backend/README.md)

#### Option B: Local Development
```bash
# Enable dedicated metrics server (default: False)
export PROMETHEUS_METRICS_ENABLED=True

# Set custom metrics port (default: 8001)
# IMPORTANT: This port must match the port in monitoring/prometheus.yml
export PROMETHEUS_METRICS_PORT=8001

# The metrics server will automatically start on the specified port
# Access metrics at: http://localhost:8001/metrics/
# Use 0.0.0.0:8000 to allow connections from Docker containers (Prometheus)
# This binds to all IPv4 addresses, enabling Prometheus to scrape metrics
# --noreload is required because Django's auto-reloader conflicts with the dedicated metrics thread
poetry run python manage.py runserver 0.0.0.0:8000 --noreload
```

### 3. Import Dashboard in Grafana
1. Go to http://localhost:3000
2. Login: **admin** / **admin**
3. Add data source
4. Select "Prometheus". URL: `http://prometheus:9090`
5. Import Dashboard by JSON File
6. Select: `monitoring/dashboard.json`

### 4. Verify Everything Works
- **Prometheus**: http://localhost:9090 (show targets)
- **Grafana**: http://localhost:3000 (show your dashboard)
- **Metrics**: http://localhost:8001/metrics/ (show raw metrics)

## Dashboard Features

After importing the dashboard, you'll have:

- **Average Response Time by Endpoint** - Shows response time per endpoint
- **Total Calls by Endpoint** - Shows total requests per endpoint
- **Endpoint Performance Summary** - Table with:
  - Method (GET, POST, etc.)
  - Endpoint name
  - Total Calls
  - Average Response Time
  - Total Time (cumulative time per endpoint)

## Implementation Details

### Multi-Worker Gunicorn Support

The monitoring system supports multi-worker Gunicorn deployments using Prometheus' multiprocess mode.

- Each Gunicorn worker writes metrics to shared files in a designated directory (`PROMETHEUS_MULTIPROC_DIR`).
- A separate process (`utils/prometheus_aggregator.py`) reads these files and exposes aggregated metrics via HTTP.

### Configuration

#### Environment Variables
- `PROMETHEUS_METRICS_ENABLED`: Set to `true` to enable Prometheus metrics (default: `false`)
- `PROMETHEUS_METRICS_PORT`: Port for the metrics aggregator (default: `8001`)
- `PROMETHEUS_MULTIPROC_DIR`: Directory for multiprocess metric files (default: `/tmp/prometheus_multiproc_dir`)

## `prometheus.yml`
- **Target**: `host.docker.internal:8001` (backend running locally)
- **Metrics Path**: `/metrics/`
- **Scrape Interval**: 15 seconds
