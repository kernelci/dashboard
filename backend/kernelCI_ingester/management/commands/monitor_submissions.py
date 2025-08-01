from django.core.management.base import BaseCommand
import logging
import time
from kernelCI_ingester.management.commands.helpers.kcidbng_ingester import (
    cache_logs_maintenance,
    ingest_submissions_parallel,
    load_trees_name,
    verify_spool_dirs,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Monitor a folder for new files and print when found"

    def validate_args(self, max_workers) -> bool:
        if max_workers > 0:
            self.stdout.write(f"Using {max_workers} workers")
        else:
            raise ValueError("max-workers must be greater than 0")

        return True

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
            type=int,
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

    def handle(self, *args, **options):
        spool_dir = options["spool_dir"]
        interval = options["interval"]
        max_workers = options["max_workers"]
        trees_file = options.get("trees_file")

        self.stdout.write(f"Monitoring folder: {spool_dir}")
        self.stdout.write(f"Check interval: {interval} seconds")

        verify_spool_dirs(spool_dir)
        self.validate_args(max_workers=max_workers)
        trees_name = load_trees_name(trees_file_override=trees_file)

        self.stdout.write("Starting file monitoring... (Press Ctrl+C to stop)")

        try:
            while True:
                # TODO: retry failed files every x cycles
                ingest_submissions_parallel(spool_dir, trees_name, max_workers)
                cache_logs_maintenance()

                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("File monitoring stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
