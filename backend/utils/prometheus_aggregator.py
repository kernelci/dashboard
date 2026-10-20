import os
import time
from pathlib import Path

# Entrypoint runs this file as a script, so its directory is sys.path[0].
from git_mirror_size import DEFAULT_MIRROR_DIR, SIZE_FILENAME, MirrorSizeCollector
from prometheus_client import REGISTRY, start_http_server
from prometheus_client.multiprocess import MultiProcessCollector

metrics_dir = os.environ.get(
    "PROMETHEUS_MULTIPROC_DIR", "/tmp/prometheus_multiproc_dir"
)

port = int(os.environ.get("PROMETHEUS_METRICS_PORT", 8001))

os.makedirs(metrics_dir, exist_ok=True)

# Register the multi-process collector
REGISTRY.register(MultiProcessCollector(REGISTRY))
mirror_dir = Path(os.environ.get("GIT_MIRROR_DIR", DEFAULT_MIRROR_DIR))
REGISTRY.register(MirrorSizeCollector(mirror_dir / SIZE_FILENAME))

start_http_server(port)

while True:
    time.sleep(1)
