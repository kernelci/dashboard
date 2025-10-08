import os
from django_prometheus import exports


def start_development_metrics_server():
    """
    This function is intended for development use only and should not be used
    in production environments with multi-worker setups.
    """
    try:
        port = int(os.environ.get("PROMETHEUS_METRICS_PORT", 8001))
        exports.SetupPrometheusEndpointOnPort(port, addr="0.0.0.0")
        print(f"Development metrics server started on port {port}")
    except Exception as e:
        # The OSError exception (port in use) can happen with the Django reloader,
        # but the --noreload prevents it.
        print(f"Failed to start development metrics server: {e}")
