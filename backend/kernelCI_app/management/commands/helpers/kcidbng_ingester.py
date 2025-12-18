import multiprocessing
from multiprocessing.sharedctypes import Synchronized
from multiprocessing.synchronize import Lock as ProcessLock
from os import DirEntry
import json
import logging
import os
from queue import Queue
from typing_extensions import Literal
from kernelCI_app.constants.ingester import (
    CONVERT_LOG_EXCERPT,
    INGEST_BATCH_SIZE,
    INGEST_FILES_BATCH_SIZE,
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
    aggregate_checkouts_and_pendings,
)
from django.db import connections, transaction
from kernelCI_app.models import Issues, Checkouts, Builds, Tests, Incidents

from kernelCI_app.management.commands.helpers.process_submissions import (
    TableNames,
    build_instances_from_submission,
)
from kernelCI_app.typeModels.modelTypes import TableModels

from prometheus_client import Counter

type INGESTER_DIRS = Literal["archive", "failed", "pending_retry"]


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
) -> tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]:
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
    buffer_files: set[tuple[str, str]],
    dirs: dict[INGESTER_DIRS, str],
    stat_ok: Synchronized,
    stat_fail: Synchronized,
    counter_lock: ProcessLock,
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
            aggregate_checkouts_and_pendings(
                checkouts_instances=checkouts_buf,
                tests_instances=tests_buf,
                build_instances=builds_buf,
            )
        for filename, filepath in buffer_files:
            os.rename(filepath, os.path.join(dirs["archive"], filename))

        with counter_lock:
            stat_ok.value += len(buffer_files)
    except Exception as e:
        logger.error("Error during buffer flush: %s", e)
        try:
            for filename, filepath in buffer_files:
                os.rename(filepath, os.path.join(dirs["failed"], filename))
            out("Moved %d files to pending retry directory" % len(buffer_files))
            with counter_lock:
                stat_fail.value += len(buffer_files)
        except OSError as oe:
            logger.error("OS error during buffer file pending retry move: %s", oe)
            logger.error("Removing files from buffer set, they should be retried")
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
        buffer_files.clear()


MAP_TABLENAMES_TO_COUNTER: dict[TableNames, Counter] = {
    "checkouts": CHECKOUTS_COUNTER,
    "issues": ISSUES_COUNTER,
    "builds": BUILDS_COUNTER,
    "tests": TESTS_COUNTER,
    "incidents": INCIDENTS_COUNTER,
}


class SubmissionsInstances(TypedDict):
    issues: list[Issues]
    checkouts: list[Checkouts]
    builds: list[Builds]
    tests: list[Tests]
    incidents: list[Incidents]


def process_batch(
    process_queue: Queue,
    tree_names: dict[str, str],
    dirs: dict[INGESTER_DIRS, str],
    processed: Synchronized,
    stat_ok: Synchronized,
    stat_fail: Synchronized,
    counter_lock: ProcessLock,
) -> None:
    # Ensure that the new process has a unique connection to the database
    connections.close_all()

    instances_dict: SubmissionsInstances = {
        "issues": [],
        "checkouts": [],
        "builds": [],
        "tests": [],
        "incidents": [],
    }

    buffer_files = set()

    while True:
        batch = process_queue.get()

        if batch is None or len(batch) == 0:
            break

        for file in batch:
            data, metadata = prepare_file_data(file, tree_names)

            if metadata and metadata.get("error"):
                try:
                    move_file_to_failed_dir(file["path"], dirs["failed"])
                except Exception:
                    pass
                with counter_lock:
                    stat_fail.value += 1
                    processed.value += 1
                continue

            if data is None:
                with counter_lock:
                    processed.value += 1
                continue

            with counter_lock:
                processed.value += 1
            FILES_INGESTER_COUNTER.labels(ingester=INGESTER_GRAFANA_LABEL).inc()

            instances = build_instances_from_submission(data, MAP_TABLENAMES_TO_COUNTER)

            instances_dict["issues"].extend(instances["issues"])
            instances_dict["checkouts"].extend(instances["checkouts"])
            instances_dict["builds"].extend(instances["builds"])
            instances_dict["tests"].extend(instances["tests"])
            instances_dict["incidents"].extend(instances["incidents"])

            buffer_files.add((file["name"], file["path"]))

        # Sort instances to prevent deadlocks when multiple transactions update the same rows
        instances_dict["issues"].sort(key=lambda x: x.id)
        instances_dict["checkouts"].sort(key=lambda x: x.id)
        instances_dict["builds"].sort(key=lambda x: x.id)
        instances_dict["tests"].sort(key=lambda x: x.id)
        instances_dict["incidents"].sort(key=lambda x: x.id)

        flush_buffers(
            issues_buf=(
                instances_dict["issues"]
                if len(instances_dict["issues"]) >= INGEST_BATCH_SIZE
                else []
            ),
            checkouts_buf=(
                instances_dict["checkouts"]
                if len(instances_dict["checkouts"]) >= INGEST_BATCH_SIZE
                else []
            ),
            builds_buf=(
                instances_dict["builds"]
                if len(instances_dict["builds"]) >= INGEST_BATCH_SIZE
                else []
            ),
            tests_buf=(
                instances_dict["tests"]
                if len(instances_dict["tests"]) >= INGEST_BATCH_SIZE
                else []
            ),
            incidents_buf=(
                instances_dict["incidents"]
                if len(instances_dict["incidents"]) >= INGEST_BATCH_SIZE
                else []
            ),
            buffer_files=buffer_files,
            dirs=dirs,
            stat_ok=stat_ok,
            stat_fail=stat_fail,
            counter_lock=counter_lock,
        )

    if any(len(instances_dict[table]) for table in instances_dict):  # type: ignore
        out("Process finished, flushing remaining buffers")
        flush_buffers(
            issues_buf=instances_dict["issues"],
            checkouts_buf=instances_dict["checkouts"],
            builds_buf=instances_dict["builds"],
            tests_buf=instances_dict["tests"],
            incidents_buf=instances_dict["incidents"],
            buffer_files=buffer_files,
            dirs=dirs,
            stat_ok=stat_ok,
            stat_fail=stat_fail,
            counter_lock=counter_lock,
        )


def print_ingest_progress(
    processed: int,
    total_files: int,
    total_bytes: int,
    stat_ok: int,
    stat_fail: int,
    elapsed: float,
    queue_size: int,
) -> None:
    """
    Print a report of the ingestion process.
    """
    files_per_sec = total_files / elapsed if elapsed > 0 else 0.0
    mb = total_bytes / (1024 * 1024)
    mb_per_sec = mb / elapsed if elapsed > 0 else 0.0
    rate = processed / elapsed if elapsed > 0 else 0.0
    remaining = total_files - processed
    eta = remaining / rate if rate > 0 else float("inf")

    if remaining > 0:
        msg = (
            "Progress: %d/%d files (ok=%d, fail=%d) | "
            "%.2fs elapsed | %.1f files/s | ETA %.1fs | Queue size: %d"
            % (
                processed,
                total_files,
                stat_ok,
                stat_fail,
                elapsed,
                rate,
                eta,
                queue_size,
            )
        )
    else:
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


def ingest_submissions_parallel(  # noqa: C901 - orchestrator with IO + multiprocessing
    json_files: list[DirEntry[str]],
    tree_names: dict[str, str],
    dirs: dict[INGESTER_DIRS, str],
    max_workers: int = 5,
) -> None:
    """
    Ingest submissions in parallel using child processes for I/O and database operations.
    """
    cycle_start = time.time()
    total_bytes = 0
    total_files_count = len(json_files)

    process_queue: multiprocessing.Queue[Optional[list[SubmissionFileMetadata]]] = (
        multiprocessing.Queue(maxsize=INGEST_QUEUE_MAXSIZE)
    )

    batch = []
    for file in json_files:
        try:
            total_bytes += file.stat().st_size
        except Exception:
            pass

        batch.append(
            SubmissionFileMetadata(
                path=file.path,
                name=file.name,
                size=file.stat().st_size,
            )
        )

        batch_len = len(batch)
        if batch_len >= INGEST_FILES_BATCH_SIZE or batch_len >= total_files_count:
            process_queue.put(batch)
            batch = []

    out(
        "Spool status: %d .json files queued (%.2f MB)"
        % (
            len(json_files),
            total_bytes / (1024 * 1024) if total_bytes else 0.0,
        )
    )

    stat_ok = multiprocessing.Value("i", 0)
    stat_fail = multiprocessing.Value("i", 0)
    counter_lock = multiprocessing.Lock()
    processed = multiprocessing.Value("i", 0)
    last_progress = cycle_start
    progress_every_sec = 2.0

    writers = []
    try:
        for _ in range(max_workers):
            writer = multiprocessing.Process(
                target=process_batch,
                args=(
                    process_queue,
                    tree_names,
                    dirs,
                    processed,
                    stat_ok,
                    stat_fail,
                    counter_lock,
                ),
            )
            writers.append(writer)
            writer.start()
            process_queue.put(None)  # Poison pill to signal the end of the queue

        while not process_queue.empty():
            if time.time() - last_progress > progress_every_sec:
                print_ingest_progress(
                    processed.value,
                    total_files_count,
                    total_bytes,
                    stat_ok.value,
                    stat_fail.value,
                    time.time() - cycle_start,
                    process_queue.qsize(),
                )
                last_progress = time.time()
            time.sleep(1)

        for writer in writers:
            writer.join()
    except KeyboardInterrupt:
        out("\nKeyboardInterrupt: terminating workers...")
        for writer in writers:
            if writer.is_alive():
                writer.terminate()
        for writer in writers:
            writer.join()
        out("Workers terminated.")

    elapsed = time.time() - cycle_start
    total_files = total_files_count
    print_ingest_progress(
        processed.value,
        total_files,
        total_bytes,
        stat_ok.value,
        stat_fail.value,
        elapsed,
        process_queue.qsize(),
    )
