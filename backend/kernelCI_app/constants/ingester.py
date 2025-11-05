"""Constant settings for the ingester functions"""

import os
import logging
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

TREES_FILE = "/app/trees.yaml"


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
