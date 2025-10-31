import argparse
from django.core.management.base import BaseCommand
import logging
import time
import os
from kernelCI_app.management.commands.helpers.kcidbng_ingester import (
    ingest_submissions_parallel,
)
from kernelCI_app.management.commands.helpers.file_utils import (
    load_tree_names,
    verify_spool_dirs,
)
from kernelCI_app.management.commands.helpers.log_excerpt_utils import (
    cache_logs_maintenance,
)

logger = logging.getLogger(__name__)


def check_positive_int(value) -> bool:
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s has to be greater than 0" % value)
    return ivalue


class Command(BaseCommand):
    help = "Monitor a folder for new files and print when found"

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
        archive_dir = os.path.join(spool_dir, "archive")
        failed_dir = os.path.join(spool_dir, "failed")

        self.stdout.write(f"Monitoring folder: {spool_dir}")
        self.stdout.write(f"Archive directory: {archive_dir}")
        self.stdout.write(f"Failed directory: {failed_dir}")
        self.stdout.write(f"Check interval: {interval} seconds")
        self.stdout.write(f"Using {max_workers} workers")

        verify_spool_dirs(spool_dir)
        tree_names = load_tree_names(trees_file=trees_file)

        self.stdout.write("Starting file monitoring... (Press Ctrl+C to stop)")

        try:
            while True:
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
                if len(json_files) > 0:
                    ingest_submissions_parallel(
                        json_files, tree_names, archive_dir, failed_dir, max_workers
                    )
                cache_logs_maintenance()

                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("File monitoring stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
