"""Constant settings for the ingester functions"""

import os
import logging
import re
from kernelCI_app.constants.tree_names import TREE_NAMES_FILENAME
from utils.validation import is_boolean_or_string_true

logger = logging.getLogger("ingester")


VERBOSE: bool = is_boolean_or_string_true(os.environ.get("VERBOSE", False))
"""Variable used to toggle info logs. Default: False"""

CONVERT_LOG_EXCERPT = is_boolean_or_string_true(
    os.environ.get("CONVERT_LOG_EXCERPT", False)
)
"""Toggle to convert the log_excerpt to output_files url. Default: False"""

LOGEXCERPT_THRESHOLD = int(os.environ.get("LOGEXCERPT_THRESHOLD", 256))
"""Bytes threshold for log_excerpt to be converted to url. Default: 256"""

STORAGE_TOKEN = os.environ.get("STORAGE_TOKEN", None)
STORAGE_BASE_URL = os.environ.get(
    "STORAGE_BASE_URL", "https://files-staging.kernelci.org"
)
UPLOAD_URL = f"{STORAGE_BASE_URL}/upload"

CACHE_LOGS_SIZE_LIMIT = int(os.environ.get("CACHE_LOGS_SIZE_LIMIT", 100000))
"""Arbitrary limit for cache_logs size, adjust as needed. Default: 100000"""

INGESTER_TREES_FILEPATH = f"/app/{TREE_NAMES_FILENAME}"

INGESTER_GRAFANA_LABEL = "django"

PROMETHEUS_MULTIPROC_DIR = os.environ.get("PROMETHEUS_MULTIPROC_DIR")
"""
Directory for Prometheus multiprocess metric files. Default: None
PROMETHEUS_MULTIPROC_DIR must be set for Prometheus multiprocess metrics to be collected correctly.
See https://prometheus.github.io/client_python/multiprocess/ for more details.
"""

INGEST_FILES_BATCH_SIZE = int(os.environ.get("INGEST_FILES_BATCH_SIZE", 100))
"""Size of the batch of files to be queued. Default: 100"""

try:
    INGESTER_METRICS_PORT = int(os.environ.get("INGESTER_METRICS_PORT", 8002))
except (ValueError, TypeError):
    logger.warning("Invalid INGESTER_METRICS_PORT, using default 8002")
    INGESTER_METRICS_PORT = 8002

# Batching and backpressure controls
try:
    INGEST_BATCH_SIZE = int(os.environ.get("INGEST_BATCH_SIZE", "10000"))
except (ValueError, TypeError):
    logger.warning("Invalid INGEST_BATCH_SIZE, using default 10000")
    INGEST_BATCH_SIZE = 10000

try:
    INGEST_FLUSH_TIMEOUT_SEC = float(os.environ.get("INGEST_FLUSH_TIMEOUT_SEC", "2.0"))
except (ValueError, TypeError):
    logger.warning("Invalid INGEST_FLUSH_TIMEOUT_SEC, using default 2.0")
    INGEST_FLUSH_TIMEOUT_SEC = 2.0

try:
    INGEST_QUEUE_MAXSIZE = int(os.environ.get("INGEST_QUEUE_MAXSIZE", "5000"))
except (ValueError, TypeError):
    logger.warning("Invalid INGEST_QUEUE_MAXSIZE, using default 5000")
    INGEST_QUEUE_MAXSIZE = 5000

AUTOMATIC_LABS = re.compile(r"^(shell|k8s.*)$")
"""Regex pattern to find labs that were named automatically and should not be in the real lab/runtime field"""
AUTOMATIC_LAB_FIELD = "automatic_lab"
"""Field name where automatic lab names will be moved to"""
