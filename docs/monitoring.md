# Monitoring and Metrics

This document explains how to use the monitoring system in the KernelCI Dashboard project.

## Quick Start

### 1. Start Monitoring Services
```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

### 2. Configure Metrics Server
```bash
# Enable dedicated metrics server (default: False)
export PROMETHEUS_METRICS_ENABLED=True

# Set custom metrics port (default: 8001)
# IMPORTANT: This port must match the port in monitoring/prometheus.yml
export PROMETHEUS_METRICS_PORT=8001

# The metrics server will automatically start on the specified port
# Access metrics at: http://localhost:8001/metrics/
```

### 3. Start Your Backend (First follow [backend/README.md](../backend/README.md))
```bash
# Use 0.0.0.0:8000 to allow connections from Docker containers (Prometheus)
# This binds to all IPv4 addresses, enabling Prometheus to scrape metrics
# --noreload is required because Django's auto-reloader conflicts with the dedicated metrics thread
poetry run python manage.py runserver 0.0.0.0:8000 --noreload
```

### 4. Import Dashboard in Grafana
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

## `prometheus.yml`
- **Target**: `host.docker.internal:8001` (backend running locally)
- **Metrics Path**: `/metrics/`
- **Scrape Interval**: 15 seconds
