import argparse
import logging
import os
import shutil
import signal
import time

from django.core.management.base import BaseCommand, CommandError
from prometheus_client import CollectorRegistry, Gauge, multiprocess, start_http_server

from kernelCI_app.constants.ingester import (
    INGEST_CYCLE_BATCH_SIZE,
    INGESTER_GRAFANA_LABEL,
    INGESTER_METRICS_PORT,
    PROMETHEUS_MULTIPROC_DIR,
)
from kernelCI_app.management.commands.helpers.file_utils import (
    load_tree_names,
    sweep_pending_retry,
    verify_spool_dirs,
)
from kernelCI_app.management.commands.helpers.kcidbng_ingester import (
    INGESTER_DIRS,
    ingest_submissions_parallel,
)
from kernelCI_app.management.commands.helpers.log_excerpt_utils import (
    cache_logs_maintenance,
)

logger = logging.getLogger(__name__)


QUEUE_SIZE_GAUGE = Gauge(
    "kcidb_ingestion_queue",
    "Number of files in queue to be ingested",
    ["ingester"],
    multiprocess_mode="livemax",
)


PENDING_RETRY_GAUGE = Gauge(
    "kcidb_ingestion_pending_retry",
    "Number of submissions waiting to be ingested again after a deferred failure",
    ["ingester"],
    multiprocess_mode="livemax",
)

RETRY_SWEEP_INTERVAL_SEC = 300
RETRY_SWEEP_MAX_INTERVAL_SEC = 1800
RETRY_SWEEP_LIMIT = 5000
STALL_GRACE_MINUTES = int(os.environ.get("INGESTER_STALL_GRACE_MINUTES", 60))


def check_positive_int(value) -> bool:
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s has to be greater than 0" % value)
    return ivalue


class Command(BaseCommand):
    help = "Monitor a folder for new files and print when found"
    running = True

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully when running on Docker"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False

    def _setup_prometheus(self):
        if PROMETHEUS_MULTIPROC_DIR:
            if os.path.exists(PROMETHEUS_MULTIPROC_DIR):
                shutil.rmtree(PROMETHEUS_MULTIPROC_DIR)

            os.makedirs(PROMETHEUS_MULTIPROC_DIR, exist_ok=True)
            registry = CollectorRegistry()
            multiprocess.MultiProcessCollector(registry)
            start_http_server(INGESTER_METRICS_PORT, registry=registry)
        else:
            logger.warning(
                "PROMETHEUS_MULTIPROC_DIR is not set, skipping Prometheus metrics"
            )

    def _scan_spool_dir(self, spool_dir: str) -> list[str]:
        """Scan spool directory, returning only path strings to keep memory bounded."""
        try:
            with os.scandir(spool_dir) as it:
                cached_paths = [
                    entry.path
                    for entry in it
                    if entry.is_file() and entry.name.endswith(".json")
                ]
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            self.stdout.write(
                f"[{ts}] Spool scan: {len(cached_paths)} .json files pending"
            )
            return cached_paths
        except PermissionError:
            logger.error(
                "Permission denied scanning spool directory: %s",
                spool_dir,
                exc_info=True,
            )
            self.running = False
            return []
        except OSError:
            logger.warning(
                "Transient OS error scanning spool directory: %s",
                spool_dir,
                exc_info=True,
            )
            return []

    @staticmethod
    def _count_json_files(directory: str) -> int:
        try:
            with os.scandir(directory) as it:
                return sum(1 for e in it if e.is_file() and e.name.endswith(".json"))
        except OSError:
            return 0

    def add_arguments(self, parser):
        # TODO: add a way to set the folder by env var instead of by argument
        parser.add_argument(
            "--spool-dir",
            type=str,
            required=True,
            help="Path to the spool directory with the json files and failed/archive subfolders",
        )
        parser.add_argument(
            "--max-workers",
            type=check_positive_int,
            default=5,
            help="Maximum number of workers to process files in parallel (default: 5)",
        )
        parser.add_argument(
            "--interval",
            type=int,
            default=5,
            help="Check interval in seconds (default: 5)",
        )
        parser.add_argument(
            "--trees-file",
            type=str,
            help="""Path to the file relating tree names with their URL.
             Use only to override the default path.""",
        )

    def handle(
        self,
        *args,
        spool_dir: str,
        max_workers: int,
        interval: int,
        trees_file: str,
        **options,
    ):
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

        self._setup_prometheus()

        dirs: dict[INGESTER_DIRS, str] = {
            "archive": os.path.join(spool_dir, "archive"),
            "failed": os.path.join(spool_dir, "failed"),
            "pending_retry": os.path.join(spool_dir, "pending_retry"),
        }

        self.stdout.write(f"Monitoring folder: {spool_dir}")
        self.stdout.write(f"Archive directory: {dirs['archive']}")
        self.stdout.write(f"Failed directory: {dirs['failed']}")
        self.stdout.write(f"Pending retry directory: {dirs['pending_retry']}")
        self.stdout.write(f"Check interval: {interval} seconds")
        self.stdout.write(f"Using {max_workers} workers")

        verify_spool_dirs(spool_dir)
        tree_names = load_tree_names(trees_file=trees_file)

        self.stdout.write("Starting file monitoring... (Press Ctrl+C to stop)")

        cached_files: list[str] = []
        cache_pos = 0
        last_sweep = 0.0
        stalled_since = None
        backlog_floor = 0

        try:
            while self.running:
                # Requeue deferred submissions once the spool is drained, so
                # they never delay new ones, and eventually regardless in case
                # it never drains.
                spool_drained = cache_pos >= len(cached_files)
                since_sweep = time.time() - last_sweep
                if (spool_drained and since_sweep >= RETRY_SWEEP_INTERVAL_SEC) or (
                    since_sweep >= RETRY_SWEEP_MAX_INTERVAL_SEC
                ):
                    # Measured before the sweep, otherwise requeueing looks
                    # like the backlog draining.
                    backlog = self._count_json_files(dirs["pending_retry"])
                    PENDING_RETRY_GAUGE.labels(INGESTER_GRAFANA_LABEL).set(backlog)

                    if backlog == 0:
                        stalled_since = None
                        backlog_floor = 0
                    elif stalled_since is None or backlog < backlog_floor:
                        stalled_since = time.time()
                        backlog_floor = backlog
                        logger.error(
                            "%d submissions deferred for retry; will exit if the "
                            "backlog does not shrink within %d minutes",
                            backlog,
                            STALL_GRACE_MINUTES,
                        )
                    elif time.time() - stalled_since > STALL_GRACE_MINUTES * 60:
                        raise CommandError(
                            f"Ingester stalled: {backlog} submissions waiting in "
                            f"{dirs['pending_retry']} for over "
                            f"{STALL_GRACE_MINUTES} minutes without the backlog "
                            "shrinking. Nothing is lost, they are ingested once "
                            "the cause is fixed. See the flush errors above."
                        )

                    requeued = sweep_pending_retry(
                        spool_dir, dirs["pending_retry"], RETRY_SWEEP_LIMIT
                    )
                    last_sweep = time.time()
                    if requeued:
                        self.stdout.write(f"Requeued {requeued} deferred submissions")

                # Only re-scan directory when cache is depleted
                if cache_pos >= len(cached_files):
                    cached_files = self._scan_spool_dir(spool_dir)
                    cache_pos = 0

                remaining = len(cached_files) - cache_pos
                QUEUE_SIZE_GAUGE.labels(INGESTER_GRAFANA_LABEL).set(remaining)

                if remaining > 0:
                    end = min(cache_pos + INGEST_CYCLE_BATCH_SIZE, len(cached_files))
                    batch = cached_files[cache_pos:end]
                    cache_pos = end
                    self.stdout.write(
                        f"Processing {len(batch)} files"
                        f" ({len(cached_files) - cache_pos}"
                        " remaining in cache)"
                    )
                    ingest_submissions_parallel(
                        batch,
                        tree_names,
                        dirs,
                        max_workers,
                    )

                cache_logs_maintenance()

                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("File monitoring stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
        finally:
            logger.info("File monitoring shutdown complete")
