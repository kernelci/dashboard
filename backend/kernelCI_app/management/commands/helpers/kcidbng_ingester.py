import multiprocessing
from multiprocessing.synchronize import Event as EventClass
from os import DirEntry
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import logging
import os
from queue import Queue, Empty
from kernelCI_app.constants.ingester import (
    CONVERT_LOG_EXCERPT,
    INGEST_BATCH_SIZE,
    INGEST_FLUSH_TIMEOUT_SEC,
    INGEST_QUEUE_MAXSIZE,
    INGESTER_GRAFANA_LABEL,
    VERBOSE,
)
import time
import traceback
from typing import Any, Optional, TypedDict
from kernelCI_app.helpers.logger import out
from kernelCI_app.management.commands.generated.insert_queries import INSERT_QUERIES
from kernelCI_app.management.commands.helpers.file_utils import move_file_to_failed_dir
from kernelCI_app.management.commands.helpers.log_excerpt_utils import (
    extract_log_excerpt,
)
import kcidb_io
from kernelCI_app.management.commands.helpers.aggregation_helpers import (
    aggregate_checkouts_and_tests,
)
from django.db import connections, transaction
from kernelCI_app.models import Issues, Checkouts, Builds, Tests, Incidents

from kernelCI_app.management.commands.helpers.process_submissions import (
    TableNames,
    build_instances_from_submission,
)
from kernelCI_app.typeModels.modelTypes import TableModels

from prometheus_client import Counter


class SubmissionMetadata(TypedDict):
    filename: str
    full_filename: str
    fsize: int | None
    processing_time: float | None
    error: str | None


class SubmissionFileMetadata(TypedDict):
    path: str
    name: str
    size: int


logger = logging.getLogger("ingester")


FILES_INGESTER_COUNTER = Counter(
    "kcidb_ingestions", "Number of files ingested", ["ingester"]
)

CHECKOUTS_COUNTER = Counter(
    "kcidb_checkouts", "Number of checkouts ingested", ["ingester", "origin"]
)
ISSUES_COUNTER = Counter(
    "kcidb_issues", "Number of issues ingested", ["ingester", "origin"]
)
BUILDS_COUNTER = Counter(
    "kcidb_builds", "Number of builds ingested", ["ingester", "origin", "lab"]
)
TESTS_COUNTER = Counter(
    "kcidb_tests", "Number of tests ingested", ["ingester", "origin", "lab", "platform"]
)
INCIDENTS_COUNTER = Counter(
    "kcidb_incidents", "Number of incidents ingested", ["ingester", "origin"]
)


def standardize_tree_names(
    input_data: dict[str, Any], tree_names: dict[str, str]
) -> None:
    """
    Standardize tree names in input data using the provided mapping
    """

    checkouts: list[dict[str, Any]] = input_data.get("checkouts", [])

    for checkout in checkouts:
        git_url = checkout.get("git_repository_url")
        if git_url in tree_names:
            correct_tree = tree_names[git_url]
            if checkout.get("tree_name") != correct_tree:
                checkout["tree_name"] = correct_tree


def prepare_file_data(
    file: SubmissionFileMetadata, tree_names: dict[str, str]
) -> tuple[Optional[dict[str, Any]], dict[str, Any]]:
    """
    Prepare file data: read, extract log excerpts, standardize tree names, validate.
    This function does everything except the actual database load.

    Returns `data, metadata`.
    If an error happens, `data` will be None; if file is empty, both are None.
    """
    fsize = file["size"]

    if fsize == 0:
        if VERBOSE:
            logger.info("File %s is empty, skipping, deleting", file["path"])
        os.remove(file["path"])
        return None, None

    start_time = time.time()
    if VERBOSE:
        logger.info("Processing file %s, size: %d", file["name"], fsize)

    try:
        with open(file["path"], "r") as f:
            data = json.loads(f.read())

        # These operations can be done in parallel (especially extract_log_excerpt)
        if CONVERT_LOG_EXCERPT:
            extract_log_excerpt(data)
        standardize_tree_names(data, tree_names)
        kcidb_io.schema.V5_3.validate(data)
        kcidb_io.schema.V5_3.upgrade(data)

        processing_time = time.time() - start_time
        return data, {
            "fsize": fsize,
            "processing_time": processing_time,
        }
    except Exception as e:
        logger.error("Error preparing data from %s: %s", file["name"], e)
        logger.error(traceback.format_exc())
        return None, {
            "error": str(e),
        }


def consume_buffer(buffer: list[TableModels], table_name: TableNames) -> None:
    """
    Consume a buffer of items and insert them into the database.
    This function is called by the db_worker thread.
    """
    if not buffer:
        return

    insert_props = INSERT_QUERIES[table_name]
    updateable_model_fields = insert_props["updateable_model_fields"]
    query = insert_props["query"]

    params = []
    for obj in buffer:
        obj_values = []
        for field in updateable_model_fields:
            value = getattr(obj, field)
            model_field = obj._meta.get_field(field)
            if model_field.get_internal_type() == "JSONField" and value is not None:
                value = json.dumps(value)
            obj_values.append(value)
        params.append(tuple(obj_values))

    t0 = time.time()
    with connections["default"].cursor() as cursor:
        cursor.executemany(query, params)

    out("bulk_create %s: n=%d in %.3fs" % (table_name, len(buffer), time.time() - t0))


def flush_buffers(
    *,
    issues_buf: list[Issues],
    checkouts_buf: list[Checkouts],
    builds_buf: list[Builds],
    tests_buf: list[Tests],
    incidents_buf: list[Incidents],
) -> None:
    """
    Consumes the list of objects and tries to insert them into the database.
    """
    total = (
        len(issues_buf)
        + len(checkouts_buf)
        + len(builds_buf)
        + len(tests_buf)
        + len(incidents_buf)
    )

    if total == 0:
        return

    # Insert in dependency-safe order
    flush_start = time.time()
    try:
        # Single transaction for all tables in the flush
        with transaction.atomic():
            consume_buffer(issues_buf, "issues")
            consume_buffer(checkouts_buf, "checkouts")
            consume_buffer(builds_buf, "builds")
            consume_buffer(tests_buf, "tests")
            consume_buffer(incidents_buf, "incidents")
            aggregate_checkouts_and_tests(
                checkouts_instances=checkouts_buf,
                tests_instances=tests_buf,
            )
    except Exception as e:
        logger.error("Error during buffer flush: %s", e)
    finally:
        flush_dur = time.time() - flush_start
        rate = total / flush_dur if flush_dur > 0 else 0.0
        msg = (
            "Flushed batch in %.3fs (%.1f items/s): "
            "issues=%d checkouts=%d builds=%d tests=%d incidents=%d"
            % (
                flush_dur,
                rate,
                len(issues_buf),
                len(checkouts_buf),
                len(builds_buf),
                len(tests_buf),
                len(incidents_buf),
            )
        )
        out(msg)
        issues_buf.clear()
        checkouts_buf.clear()
        builds_buf.clear()
        tests_buf.clear()
        incidents_buf.clear()


# TODO: lower the complexity of this function
def db_worker(stop_event: EventClass, db_queue: Queue) -> None:  # noqa: C901
    """
    Worker process that processes the database queue.
    This is the only process that interacts with the database.

    Args:
        stop_event: multiprocessing.Event (flag) to signal the worker to stop processing
        queue: multiprocessing.JoinableQueue to communicate with the worker
    """

    # Local buffers for batching
    issues_buf: list[Issues] = []
    checkouts_buf: list[Checkouts] = []
    builds_buf: list[Builds] = []
    tests_buf: list[Tests] = []
    incidents_buf: list[Incidents] = []

    last_flush_ts = time.time()

    def buffered_total() -> int:
        return (
            len(issues_buf)
            + len(checkouts_buf)
            + len(builds_buf)
            + len(tests_buf)
            + len(incidents_buf)
        )

    while not stop_event.is_set() or not db_queue.empty():
        try:
            item = db_queue.get(timeout=0.1)
            if item is None:
                db_queue.task_done()
                break
            try:
                filename, inst = item
                if inst is not None:
                    issues_buf.extend(inst["issues"])
                    checkouts_buf.extend(inst["checkouts"])
                    builds_buf.extend(inst["builds"])
                    tests_buf.extend(inst["tests"])
                    incidents_buf.extend(inst["incidents"])

                if buffered_total() >= INGEST_BATCH_SIZE:
                    flush_buffers(
                        issues_buf=issues_buf,
                        checkouts_buf=checkouts_buf,
                        builds_buf=builds_buf,
                        tests_buf=tests_buf,
                        incidents_buf=incidents_buf,
                    )
                    last_flush_ts = time.time()

                if VERBOSE:
                    msg = (
                        "Queued from %s: "
                        "issues=%d checkouts=%d builds=%d tests=%d incidents=%d"
                        % (
                            filename,
                            len(inst["issues"]),
                            len(inst["checkouts"]),
                            len(inst["builds"]),
                            len(inst["tests"]),
                            len(inst["incidents"]),
                        )
                    )
                    out(msg)
            except Exception as e:
                logger.error("Error processing item in db_worker: %s", e)
            finally:
                db_queue.task_done()

        except Empty:
            # Time-based flush when idle
            if (time.time() - last_flush_ts) >= INGEST_FLUSH_TIMEOUT_SEC:
                if VERBOSE:
                    out(
                        "Idle flush after %.1fs without new items (buffered=%d)"
                        % (
                            INGEST_FLUSH_TIMEOUT_SEC,
                            buffered_total(),
                        )
                    )
                flush_buffers(
                    issues_buf=issues_buf,
                    checkouts_buf=checkouts_buf,
                    builds_buf=builds_buf,
                    tests_buf=tests_buf,
                    incidents_buf=incidents_buf,
                )
                last_flush_ts = time.time()
            continue
        except Exception as e:
            logger.error("Unexpected error in db_worker: %s", e)

    # Final flush after loop ends
    flush_buffers(
        issues_buf=issues_buf,
        checkouts_buf=checkouts_buf,
        builds_buf=builds_buf,
        tests_buf=tests_buf,
        incidents_buf=incidents_buf,
    )


MAP_TABLENAMES_TO_COUNTER: dict[TableNames, Counter] = {
    "checkouts": CHECKOUTS_COUNTER,
    "issues": ISSUES_COUNTER,
    "builds": BUILDS_COUNTER,
    "tests": TESTS_COUNTER,
    "incidents": INCIDENTS_COUNTER,
}


def process_file(
    file: SubmissionFileMetadata,
    tree_names: dict[str, str],
    failed_dir: str,
    archive_dir: str,
    db_queue: Queue,
) -> bool:
    """
    Process a single file in a process, then queue it for database insertion.

    Returns:
        True if file was processed or deleted, False if an error occured
    """
    data, metadata = prepare_file_data(file, tree_names)

    if "error" in metadata:
        try:
            move_file_to_failed_dir(file["path"], failed_dir)
        except Exception:
            pass
        return False

    if data is None:
        # Empty file, already deleted
        return True

    db_queue.put(
        (file["name"], build_instances_from_submission(data, MAP_TABLENAMES_TO_COUNTER))
    )
    FILES_INGESTER_COUNTER.labels(INGESTER_GRAFANA_LABEL).inc()

    # Archive the file after queuing (we can do this optimistically)
    try:
        os.rename(file["path"], os.path.join(archive_dir, file["name"]))
    except Exception as e:
        logger.error("Error archiving file %s: %s", file["name"], e)
        return False

    return True


def ingest_submissions_parallel(  # noqa: C901 - orchestrator with IO + threading
    json_files: list[DirEntry[str]],
    tree_names: dict[str, str],
    archive_dir: str,
    failed_dir: str,
    max_workers: int = 5,
) -> None:
    """
    Ingest submissions in parallel using ThreadPoolExecutor for I/O operations
    and a single database worker thread.
    """
    total_bytes = 0
    for f in json_files:
        try:
            total_bytes += f.stat().st_size
        except Exception:
            pass

    out(
        "Spool status: %d .json files queued (%.2f MB)"
        % (
            len(json_files),
            total_bytes / (1024 * 1024) if total_bytes else 0.0,
        )
    )

    cycle_start = time.time()
    total_files_count = len(json_files)

    manager = multiprocessing.Manager()
    db_queue = manager.JoinableQueue(maxsize=INGEST_QUEUE_MAXSIZE)

    # Start database worker process
    # This process will constantly consume the db_queue and send data to the database
    stop_event = multiprocessing.Event()
    db_process = multiprocessing.Process(target=db_worker, args=(stop_event, db_queue))
    db_process.start()

    stat_ok = 0
    stat_fail = 0

    processed = 0
    last_progress = cycle_start
    progress_every_n = 200
    progress_every_sec = 2.0

    try:
        # Process files in parallel
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all files for processing
            future_to_file = {
                executor.submit(
                    process_file,
                    {"path": file.path, "name": file.name, "size": file.stat().st_size},
                    tree_names,
                    failed_dir,
                    archive_dir,
                    db_queue,
                ): file.name
                for file in json_files
            }

            # Collect results progressively
            for future in as_completed(future_to_file):
                filename = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        stat_ok += 1
                    else:
                        stat_fail += 1
                except Exception as e:
                    logger.error("Exception processing %s: %s", filename, e)
                    stat_fail += 1
                finally:
                    processed += 1
                    now = time.time()
                    if (
                        processed % progress_every_n == 0
                        or (now - last_progress) >= progress_every_sec
                    ):
                        elapsed = now - cycle_start
                        rate = processed / elapsed if elapsed > 0 else 0.0
                        remaining = total_files_count - processed
                        eta = remaining / rate if rate > 0 else float("inf")
                        try:
                            qsz = db_queue.qsize()
                        except Exception:
                            qsz = -1
                        msg = (
                            "Progress: %d/%d files (ok=%d, fail=%d) | "
                            "%.2fs elapsed | %.1f files/s | ETA %.1fs | db_queue=%d"
                            % (
                                processed,
                                total_files_count,
                                stat_ok,
                                stat_fail,
                                elapsed,
                                rate,
                                eta,
                                qsz,
                            )
                        )
                        out(msg)
                        last_progress = now

        out("Waiting for DB queue to drain... size=%d" % db_queue.qsize())
        # Wait for all database operations to complete
        db_queue.join()

    except KeyboardInterrupt:
        out("KeyboardInterrupt: stopping ingestion and flushing...")
        try:
            # Attempt to cancel remaining futures and exit early
            # Note: this only cancels tasks not yet started
            pass
        finally:
            raise
    finally:
        # Signal database worker to stop
        stop_event.set()
        db_queue.put(None)  # Poison pill
        db_process.join()

    elapsed = time.time() - cycle_start
    total_files = stat_ok + stat_fail
    if total_files > 0:
        files_per_sec = total_files / elapsed if elapsed > 0 else 0.0
        mb = total_bytes / (1024 * 1024)
        mb_per_sec = mb / elapsed if elapsed > 0 else 0.0
        msg = (
            "Ingest cycle: %d files (ok=%d, fail=%d) in %.2fs | "
            "%.2f files/s | %.2f MB processed (%.2f MB/s)"
            % (
                total_files,
                stat_ok,
                stat_fail,
                elapsed,
                files_per_sec,
                mb,
                mb_per_sec,
            )
        )
        out(msg)
    else:
        out("No files processed, nothing to do")
