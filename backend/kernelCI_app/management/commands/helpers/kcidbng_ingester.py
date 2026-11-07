import json
import logging
import multiprocessing
import os
import signal
import time
import traceback
from ctypes import c_int
from multiprocessing.connection import Connection, wait
from multiprocessing.process import BaseProcess
from multiprocessing.synchronize import Lock as ProcessLock
from queue import Empty, Full, Queue
from typing import Any, Optional, Self, TypedDict

import kcidb_io
from django.db import connections, transaction
from prometheus_client import Counter, multiprocess
from typing_extensions import Literal

from kernelCI_app.constants.ingester import (
    AUTOMATIC_LAB_FIELD,
    AUTOMATIC_LABS,
    CONVERT_LOG_EXCERPT,
    INGEST_BATCH_SIZE,
    INGEST_FILES_BATCH_SIZE,
    INGEST_QUEUE_MAXSIZE,
    INGESTER_GRAFANA_LABEL,
    PROMETHEUS_MULTIPROC_DIR,
    VERBOSE,
)
from kernelCI_app.helpers.logger import out
from kernelCI_app.management.commands.generated.insert_queries import INSERT_QUERIES
from kernelCI_app.management.commands.helpers.aggregation_helpers import (
    aggregate_checkouts_and_pendings,
)
from kernelCI_app.management.commands.helpers.file_utils import move_file_to_failed_dir
from kernelCI_app.management.commands.helpers.log_excerpt_utils import (
    LogExcerptUploadError,
    cache_logs_maintenance,
    extract_log_excerpt,
)
from kernelCI_app.management.commands.helpers.process_submissions import (
    TableNames,
    build_instances_from_submission,
)
from kernelCI_app.models import Builds, Checkouts, Incidents, Issues, Tests
from kernelCI_app.typeModels.modelTypes import TableModels

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
WORKER_FAILURES_COUNTER = Counter(
    "kcidb_ingester_worker_failures",
    "Number of ingester worker processes that exited abnormally",
    ["ingester", "reason"],
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


def _standardize_lab_field(item: dict[str, Any], field: str) -> None:
    """
    Moves automatic lab/runtime value to AUTOMATIC_LAB_FIELD and falls back to origin.

        lab is AUTOMATIC_LAB -> fallback to origin
        lab is None -> fallback to origin
        lab is not None -> do nothing
    """
    lab = item.get("misc", {}).get(field)
    is_automatic = lab and AUTOMATIC_LABS.match(lab)
    # Real lab for the lab_id FK, captured before the origin fallback (#1752) below
    # overwrites misc, which would otherwise pollute the lab dimension.
    item["_real_lab"] = None if is_automatic else lab
    if is_automatic:
        item["misc"][AUTOMATIC_LAB_FIELD] = lab
        item["misc"].pop(field, None)
        lab = None

    if not lab or is_automatic:
        origin = item.get("origin")
        if origin:
            item.setdefault("misc", {})[field] = origin


def standardize_labs(input_data: dict[str, Any]) -> None:
    """
    Standardize labs in data, moving automatic lab names to AUTOMATIC_LAB_FIELD.
    Falls back to 'origin' when 'lab' (builds) or 'runtime' (tests) is missing.
    """
    for build in input_data.get("builds", []):
        _standardize_lab_field(build, "lab")

    for test in input_data.get("tests", []):
        _standardize_lab_field(test, "runtime")


def _extract_origins_info(data: Optional[dict[str, Any]]) -> str:
    """Extract unique origins from submissions for error reporting.

    Returns a formatted string like " [origins: origin1, origin2]" if origins
    are found, otherwise an empty string.
    """
    origins: set[str] = set()
    if data:
        for section in ("tests", "builds", "checkouts", "issues", "incidents"):
            for item in data.get(section, []):
                origin = item.get("origin")
                if origin:
                    origins.add(origin)
    return f" [origins: {', '.join(sorted(origins))}]" if origins else ""


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
        try:
            os.remove(file["path"])
        except FileNotFoundError:
            # Removed between the spool scan and this batch.
            pass
        return None, None

    start_time = time.time()
    if VERBOSE:
        logger.info("Processing file %s, size: %d", file["name"], fsize)

    data: Optional[dict[str, Any]] = None
    try:
        with open(file["path"], "r") as f:
            data = json.loads(f.read())

        # These operations can be done in parallel (especially extract_log_excerpt)
        if CONVERT_LOG_EXCERPT:
            extract_log_excerpt(data)
        standardize_tree_names(data, tree_names)
        kcidb_io.schema.V5_3.validate(data)
        kcidb_io.schema.V5_3.upgrade(data)
        standardize_labs(data)

        processing_time = time.time() - start_time
        return data, {
            "fsize": fsize,
            "processing_time": processing_time,
        }
    except LogExcerptUploadError as e:
        logger.warning("Deferring %s: %s", file["name"], e)
        return None, {"error": str(e), "retry": True}
    except Exception as e:
        origin_info = _extract_origins_info(data)
        logger.error("Error preparing data from %s%s: %s", file["name"], origin_info, e)
        logger.error(traceback.format_exc())
        return None, {
            "error": str(e),
        }


def assign_lab_ids(builds_buf: list[Builds], tests_buf: list[Tests]) -> None:
    """Resolve each instance's real lab name to a labs.id and set its lab_id FK.

    Select-first so we only INSERT genuinely new labs (avoids burning the id
    sequence on every flush). New labs are committed outside the fact-insert
    transaction (autocommit).
    """
    objs = [*builds_buf, *tests_buf]
    names = {name for obj in objs if (name := obj._lab_name)}

    id_map: dict[str, int] = {}
    if names:
        with connections["default"].cursor() as cursor:
            cursor.execute(
                "SELECT id, name FROM labs WHERE name = ANY(%s)", [list(names)]
            )
            id_map = {name: lab_id for lab_id, name in cursor.fetchall()}

            missing = [name for name in names if name not in id_map]
            if missing:
                cursor.executemany(
                    "INSERT INTO labs (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                    [(name,) for name in missing],
                )
                cursor.execute(
                    "SELECT id, name FROM labs WHERE name = ANY(%s)", [missing]
                )
                id_map.update({name: lab_id for lab_id, name in cursor.fetchall()})

    for obj in objs:
        obj.lab_id = id_map.get(obj._lab_name) if obj._lab_name else None


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
    stat_ok: c_int,
    stat_fail: c_int,
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
        # Autocommit, outside the transaction: avoids holding lab locks per flush.
        assign_lab_ids(builds_buf, tests_buf)
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
                os.rename(filepath, os.path.join(dirs["pending_retry"], filename))
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
    processed: c_int,
    stat_ok: c_int,
    stat_fail: c_int,
    counter_lock: ProcessLock,
) -> None:
    instances_dict: SubmissionsInstances = {
        "issues": [],
        "checkouts": [],
        "builds": [],
        "tests": [],
        "incidents": [],
    }

    buffer_files = set()
    parent = multiprocessing.parent_process()

    while True:
        try:
            batch = process_queue.get(timeout=1)
        except Empty:
            # A parent killed mid-cycle never sends the end-of-cycle sentinel.
            if parent is not None and not parent.is_alive():
                break
            continue

        if batch is None:
            break

        for file in batch:
            # A bad file must not take the worker down: with persistent
            # workers an unhandled exception aborts the whole command.
            try:
                data, metadata = prepare_file_data(file, tree_names)
                instances = (
                    build_instances_from_submission(data, MAP_TABLENAMES_TO_COUNTER)
                    if data is not None
                    else None
                )
            except Exception as e:
                logger.exception("Unexpected error processing %s", file["name"])
                data, metadata, instances = None, {"error": str(e)}, None

            if metadata and metadata.get("error"):
                try:
                    destination = "pending_retry" if metadata.get("retry") else "failed"
                    move_file_to_failed_dir(file["path"], dirs[destination])
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

    if any(len(instances_dict[table]) for table in instances_dict):
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


def _ingestion_worker(
    control: Connection, parent_controls: list[Connection], *batch_args
) -> None:
    # Close inherited parent endpoints so losing the parent produces EOF.
    for parent_control in parent_controls:
        parent_control.close()
    # Shutdown signals are for the parent, which finishes the cycle and then
    # sends a stop message. A signal delivered to the whole process group must
    # not abort a worker's transaction, so workers ignore it.
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    # Connections inherited through fork must not be shared with the parent.
    connections.close_all()
    try:
        while True:
            try:
                if not control.recv():
                    break
            except EOFError:
                # The parent is gone; there will be no more cycles.
                break
            try:
                process_batch(*batch_args)
            finally:
                connections.close_all()
                cache_logs_maintenance()
            try:
                control.send(None)
            except BrokenPipeError:
                # The parent is gone; nothing is left to acknowledge.
                break
    finally:
        control.close()


class IngestionWorkers:
    """Reuse writers; each cycle finishes only after every writer has flushed.

    An unexpected exit aborts the command: a dead writer may have left shared
    locks acquired. A supervisor restart creates fresh queues and locks.
    """

    def __init__(
        self,
        tree_names: dict[str, str],
        dirs: dict[INGESTER_DIRS, str],
        max_workers: int = 5,
    ) -> None:
        if max_workers < 1:
            raise ValueError("max_workers must be positive")
        # forkserver reimports models before Django is ready (Python 3.14).
        self.context = multiprocessing.get_context("fork")
        self.queue = self.context.Queue(maxsize=INGEST_QUEUE_MAXSIZE)
        # Workers serialize updates with counter_lock. Parent progress reads
        # must not block on a per-value lock abandoned by a dead worker.
        self.processed = self.context.RawValue("i", 0)
        self.stat_ok = self.context.RawValue("i", 0)
        self.stat_fail = self.context.RawValue("i", 0)
        self.counter_lock = self.context.Lock()
        self.tree_names = tree_names
        self.dirs = dirs
        self.max_workers = max_workers
        self.writers: list[BaseProcess] = []
        self.controls: list[Connection] = []

    def __enter__(self) -> Self:
        try:
            self._start_workers()
        except BaseException as exc:
            self.__exit__(type(exc), exc, exc.__traceback__)
            raise
        return self

    def _start_workers(self) -> None:
        while len(self.writers) < self.max_workers:
            control, child_control = self.context.Pipe()
            writer = self.context.Process(
                target=_ingestion_worker,
                args=(
                    child_control,
                    self.controls,
                    self.queue,
                    self.tree_names,
                    self.dirs,
                    self.processed,
                    self.stat_ok,
                    self.stat_fail,
                    self.counter_lock,
                ),
            )
            # Listed before the fork so the child closes this endpoint too.
            self.controls.append(control)
            try:
                writer.start()
            finally:
                child_control.close()
            self.writers.append(writer)

    @staticmethod
    def _log_failure(writer: BaseProcess) -> None:
        reason = "signal" if writer.exitcode < 0 else "exception"
        logger.error(
            "Worker %s exited with code %s (%s)", writer.pid, writer.exitcode, reason
        )
        WORKER_FAILURES_COUNTER.labels(
            ingester=INGESTER_GRAFANA_LABEL, reason=reason
        ).inc()

    def check_workers(self) -> None:
        failed = [writer for writer in self.writers if writer.exitcode is not None]
        if failed:
            for writer in failed:
                self._log_failure(writer)
            raise RuntimeError(
                "Ingester worker exited; restart required to retry unarchived submissions"
            )

    def _abort_worker(self, writer: BaseProcess) -> None:
        # EOF can arrive just before the exit code becomes available.
        writer.join(timeout=5)
        if writer.is_alive():
            writer.kill()
            writer.join()
        self.check_workers()

    def _put(self, batch: list[SubmissionFileMetadata] | None) -> None:
        while True:
            self.check_workers()
            try:
                self.queue.put(batch, timeout=1)
                return
            except Full:
                continue

    def ingest(self, json_files: list[str]) -> None:
        self.check_workers()
        self.processed.value = self.stat_ok.value = self.stat_fail.value = 0
        cycle_start = time.monotonic()
        total_bytes = 0
        pending: dict[Connection, BaseProcess] = {}
        for writer, control in list(zip(self.writers, self.controls, strict=True)):
            try:
                control.send(True)
            except OSError:
                self._abort_worker(writer)
            else:
                pending[control] = writer

        for offset in range(0, len(json_files), INGEST_FILES_BATCH_SIZE):
            batch = []
            for path in json_files[offset : offset + INGEST_FILES_BATCH_SIZE]:
                try:
                    size = os.path.getsize(path)
                except OSError:
                    size = 0
                total_bytes += size
                batch.append(
                    SubmissionFileMetadata(
                        path=path, name=os.path.basename(path), size=size
                    )
                )
            self._put(batch)
        for _ in self.writers:
            self._put(None)

        # A writer waits for the next start message after acknowledging its
        # sentinel, so it cannot consume another writer's end-of-cycle marker.
        # A writer that exits closes its control pipe, which reads as EOF.
        last_progress = cycle_start
        while pending:
            ready = wait([*pending, *(w.sentinel for w in self.writers)], timeout=1)
            self.check_workers()
            for control, writer in list(pending.items()):
                if control in ready:
                    try:
                        control.recv()
                    except EOFError:
                        self._abort_worker(writer)
                else:
                    continue
                del pending[control]
            now = time.monotonic()
            if not pending or now - last_progress >= 2:
                print_ingest_progress(
                    self.processed.value,
                    len(json_files),
                    total_bytes,
                    self.stat_ok.value,
                    self.stat_fail.value,
                    now - cycle_start,
                    self.queue.qsize(),
                )
                last_progress = now

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is None:
            for control in self.controls:
                try:
                    control.send(False)
                except OSError:
                    pass
        else:
            # Workers ignore SIGTERM, so only SIGKILL stops them early.
            for writer in self.writers:
                if writer.is_alive():
                    writer.kill()
        for writer in self.writers:
            writer.join(timeout=5)
            if writer.is_alive():
                writer.kill()
                writer.join()
            if exc_type is None and writer.exitcode:
                self._log_failure(writer)
            if PROMETHEUS_MULTIPROC_DIR:
                multiprocess.mark_process_dead(writer.pid)
        for control in self.controls:
            control.close()
        # A failed worker may leave unread items. Never wait for the feeder
        # thread to flush a queue whose readers have stopped.
        self.queue.cancel_join_thread()
        self.queue.close()


def ingest_submissions_parallel(
    json_files: list[str],
    tree_names: dict[str, str],
    dirs: dict[INGESTER_DIRS, str],
    max_workers: int = 5,
) -> None:
    """One-shot entry point for callers outside the long-running monitor."""
    with IngestionWorkers(tree_names, dirs, max_workers) as workers:
        workers.ingest(json_files)
