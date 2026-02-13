import argparse
import shutil
import signal
from django.core.management.base import BaseCommand
import logging
import time
import os
from kernelCI_app.management.commands.helpers.kcidbng_ingester import (
    INGESTER_DIRS,
    ingest_submissions_parallel,
)
from kernelCI_app.constants.ingester import (
    INGESTER_GRAFANA_LABEL,
    INGESTER_METRICS_PORT,
    PROMETHEUS_MULTIPROC_DIR,
)
from kernelCI_app.management.commands.helpers.file_utils import (
    load_tree_names,
    verify_spool_dirs,
)
from kernelCI_app.management.commands.helpers.log_excerpt_utils import (
    cache_logs_maintenance,
)
from prometheus_client import CollectorRegistry, Gauge, start_http_server, multiprocess

logger = logging.getLogger(__name__)


QUEUE_SIZE_GAUGE = Gauge(
    "kcidb_ingestion_queue",
    "Number of files in queue to be ingested",
    ["ingester"],
    multiprocess_mode="livemax",
)


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

        try:
            while self.running:
                # TODO: retry failed files every x cycles
                try:
                    with os.scandir(spool_dir) as it:
                        json_files = [
                            entry
                            for entry in it
                            if entry.is_file() and entry.name.endswith(".json")
                        ]
                        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        self.stdout.write(
                            f"[{ts}] Spool has {len(json_files)} .json files pending"
                        )
                except Exception:
                    pass

                QUEUE_SIZE_GAUGE.labels(INGESTER_GRAFANA_LABEL).set(len(json_files))

                if len(json_files) > 0:
                    ingest_submissions_parallel(
                        json_files,
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
