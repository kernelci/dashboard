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


def get_stall_grace_minutes() -> int:
    value = os.environ.get("INGESTER_STALL_GRACE_MINUTES", "60")
    try:
        minutes = int(value)
        if minutes > 0:
            return minutes
    except ValueError:
        pass
    raise CommandError("INGESTER_STALL_GRACE_MINUTES must be a positive integer")


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
    def _scan_pending_retry(directory: str) -> set[str]:
        try:
            with os.scandir(directory) as it:
                return {e.name for e in it if e.is_file() and e.name.endswith(".json")}
        except OSError as e:
            raise CommandError(
                f"Could not scan retry directory {directory}: {e}"
            ) from e

    def _check_retry_backlog(
        self,
        spool_dir: str,
        pending_retry_dir: str,
        retry_started: dict[str, float],
        grace_minutes: int,
    ) -> int:
        """Track each deferred file until it leaves both the retry queue and spool.

        Requeueing and new failures must not reset an older submission's clock.
        The grace period starts when this monitor first observes the failure,
        including for files left over from a previous monitor run.
        """
        pending = self._scan_pending_retry(pending_retry_dir)
        now = time.monotonic()
        for name in pending:
            if name not in retry_started:
                retry_started[name] = now
                logger.warning("Submission %s deferred for retry", name)

        for name in list(retry_started):
            if name not in pending:
                path = os.path.join(spool_dir, name)
                try:
                    os.stat(path)
                except FileNotFoundError:
                    del retry_started[name]
                    continue
                except OSError as e:
                    raise CommandError(
                        f"Could not inspect deferred file {path}: {e}"
                    ) from e

            if now - retry_started[name] > grace_minutes * 60:
                raise CommandError(
                    f"Ingester stalled: deferred submission {name} remains in "
                    f"{pending_retry_dir} or {spool_dir} for over {grace_minutes} "
                    "minutes. Nothing is lost; it can be ingested once the cause "
                    "is fixed. See the ingestion errors above."
                )
        return len(pending)

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
        grace_minutes = get_stall_grace_minutes()
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
        last_sweep = float("-inf")
        retry_started: dict[str, float] = {}

        try:
            while self.running:
                # Requeue deferred submissions once the spool is drained, so
                # they never delay new ones, and eventually regardless in case
                # it never drains.
                spool_drained = cache_pos >= len(cached_files)
                since_sweep = time.monotonic() - last_sweep
                if (spool_drained and since_sweep >= RETRY_SWEEP_INTERVAL_SEC) or (
                    since_sweep >= RETRY_SWEEP_MAX_INTERVAL_SEC
                ):
                    backlog = self._check_retry_backlog(
                        spool_dir, dirs["pending_retry"], retry_started, grace_minutes
                    )
                    PENDING_RETRY_GAUGE.labels(INGESTER_GRAFANA_LABEL).set(backlog)

                    requeued = sweep_pending_retry(
                        spool_dir, dirs["pending_retry"], RETRY_SWEEP_LIMIT
                    )
                    last_sweep = time.monotonic()
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
