import os
import time
from prometheus_client import start_http_server, REGISTRY
from prometheus_client.multiprocess import MultiProcessCollector

metrics_dir = os.environ.get(
    "PROMETHEUS_MULTIPROC_DIR", "/tmp/prometheus_multiproc_dir"
)

port = int(os.environ.get("PROMETHEUS_METRICS_PORT", 8001))

os.makedirs(metrics_dir, exist_ok=True)

# Register the multi-process collector
REGISTRY.register(MultiProcessCollector(REGISTRY))

start_http_server(port)

while True:
    time.sleep(1)
