from os import DirEntry
from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
import hashlib
import json
import logging
import os
from queue import Queue, Empty
import requests
import tempfile
import threading
import time
import traceback
from typing import Any, Literal, Optional
import yaml
import kcidb_io
from django.db import transaction
from kernelCI_app.models import Issues, Checkouts, Builds, Tests, Incidents

from kernelCI_app.management.commands.helpers.process_submissions import (
    build_instances_from_submission,
)

VERBOSE = 0
LOGEXCERPT_THRESHOLD = 256  # 256 bytes threshold for logexcerpt
CONVERT_LOG_EXCERPT = False  # If True, convert log_excerpt to output_files url

CACHE_LOGS = {}
CACHE_LOGS_SIZE_LIMIT = 100000  # Arbitrary limit for cache_logs size, adjust as needed
cache_logs_lock = threading.Lock()

STORAGE_TOKEN = os.environ.get("STORAGE_TOKEN", None)
STORAGE_BASE_URL = os.environ.get(
    "STORAGE_BASE_URL", "https://files-staging.kernelci.org"
)

TREES_FILE = "/app/trees.yaml"

logger = logging.getLogger("ingester")

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

# Thread-safe queue for database operations (bounded for backpressure)
db_queue = Queue(maxsize=INGEST_QUEUE_MAXSIZE)
db_lock = threading.Lock()


def _ts() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def _out(msg: str) -> None:
    """Write debug/perf output to stdout"""
    # logger was unreliable in some environments
    try:
        print(f"[{_ts()}] {msg}", flush=True)
    except Exception:
        pass


def move_file_to_failed_dir(filename: str, failed_dir: str) -> None:
    try:
        os.rename(filename, os.path.join(failed_dir, os.path.basename(filename)))
    except Exception as e:
        logger.error("Error moving file %s to failed directory: %s", filename, e)
        raise e


def load_tree_names(trees_file_override: Optional[str]) -> dict[str, str]:
    global TREES_FILE
    if trees_file_override is not None:
        TREES_FILE = trees_file_override

    with open(TREES_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    tree_names = {v["url"]: tree_name for tree_name, v in data.get("trees", {}).items()}

    return tree_names


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


def upload_logexcerpt(logexcerpt: str, id: str) -> str:
    """
    Upload logexcerpt to storage and return a reference(URL)
    """
    upload_url = f"{STORAGE_BASE_URL}/upload"
    if VERBOSE:
        logger.info("Uploading logexcerpt for %s to %s", id, upload_url)
    # make temporary file with logexcerpt data
    with tempfile.NamedTemporaryFile(delete=False, suffix=".logexcerpt") as temp_file:
        logexcerpt_filename = temp_file.name
        logexcerpt_compressed = gzip.compress(logexcerpt.encode("utf-8"))
        temp_file.write(logexcerpt_compressed)
        temp_file.flush()
    with open(logexcerpt_filename, "rb") as f:
        hdr = {
            "Authorization": f"Bearer {STORAGE_TOKEN}",
        }
        files = {"file0": ("logexcerpt.txt.gz", f), "path": f"logexcerpt/{id}"}
        try:
            r = requests.post(upload_url, headers=hdr, files=files)
        except Exception as e:
            logger.error("Error uploading logexcerpt for %s: %s", id, e)
            os.remove(logexcerpt_filename)
            return logexcerpt  # Return original logexcerpt if upload fails
    os.remove(logexcerpt_filename)
    if r.status_code != 200:
        logger.error(
            "Failed to upload logexcerpt for %s: %d : %s", id, r.status_code, r.text
        )
        return logexcerpt  # Return original logexcerpt if upload fails

    return f"{STORAGE_BASE_URL}/logexcerpt/{id}/logexcerpt.txt.gz"


def get_from_cache(log_hash: str) -> Optional[str]:
    """
    Check if log_hash is in the cache
    """
    with cache_logs_lock:
        return CACHE_LOGS.get(log_hash)


def set_in_cache(log_hash: str, url: str) -> None:
    """
    Set log_hash in the cache with the given URL
    """
    with cache_logs_lock:
        CACHE_LOGS[log_hash] = url
        if VERBOSE:
            logger.info("Cached log excerpt with hash %s at %s", log_hash, url)


def set_log_excerpt_ofile(item: dict[str, Any], url: str) -> dict[str, Any]:
    """
    Clean log_excerpt field
    Create name/url dict and append to output_files of job

    item is a build or test
    """
    item["log_excerpt"] = None
    data = {
        "name": "log_excerpt",
        "url": url,
    }
    if "output_files" not in item:
        item["output_files"] = []

    item["output_files"].append(data)
    return item


def process_log_excerpt_from_item(
    item: dict[str, Any], item_type: Literal["build", "test"]
) -> None:
    """
    Process log_excerpt from a single build or test (item).
    If log_excerpt is large, upload it to storage and replace with a reference.
    """
    id = item.get("id", "unknown")
    log_excerpt = item["log_excerpt"]

    if isinstance(log_excerpt, str) and len(log_excerpt) > LOGEXCERPT_THRESHOLD:
        log_hash = hashlib.sha256(log_excerpt.encode("utf-8")).hexdigest()
        if VERBOSE:
            logger.info(
                "Uploading log_excerpt for %s id %s hash %s with size %d bytes",
                item_type,
                id,
                log_hash,
                len(log_excerpt),
            )
        # check if log_excerpt already uploaded (by hash as key)
        cached_url = get_from_cache(log_hash)
        if cached_url:
            if VERBOSE:
                logger.info(
                    "Log excerpt for %s %s already uploaded, using cached URL",
                    item_type,
                    id,
                )
            set_log_excerpt_ofile(item, cached_url)
        else:
            cached_url = upload_logexcerpt(log_excerpt, log_hash)
            set_in_cache(log_hash, cached_url)
            set_log_excerpt_ofile(item, cached_url)


def extract_log_excerpt(input_data: dict[str, Any]) -> None:
    """
    Extract log_excerpt from builds and tests, if it is large,
    upload to storage and replace with a reference.
    """
    if not STORAGE_TOKEN:
        logger.warning("STORAGE_TOKEN is not set, log_excerpts will not be uploaded")
        return

    builds: list[dict[str, Any]] = input_data.get("builds", [])
    tests: list[dict[str, Any]] = input_data.get("tests", [])

    for build in builds:
        if build.get("log_excerpt"):
            process_log_excerpt_from_item(item=build, item_type="build")

    for test in tests:
        if test.get("log_excerpt"):
            process_log_excerpt_from_item(item=test, item_type="test")


def prepare_file_data(
    file: DirEntry[str], tree_names: dict[str, str]
) -> tuple[Optional[dict[str, Any]], dict[str, Any]]:
    """
    Prepare file data: read, extract log excerpts, standardize tree names, validate.
    This function does everything except the actual database load.
    """
    fsize = file.stat().st_size

    if fsize == 0:
        if VERBOSE:
            logger.info("File %s is empty, skipping, deleting", file.path)
        os.remove(file.path)
        return None, None

    start_time = time.time()
    if VERBOSE:
        logger.info("Processing file %s, size: %d", file.name, fsize)

    try:
        with open(file.path, "r") as f:
            data = json.loads(f.read())

        # These operations can be done in parallel (especially extract_log_excerpt)
        if CONVERT_LOG_EXCERPT:
            extract_log_excerpt(data)
        standardize_tree_names(data, tree_names)
        kcidb_io.schema.V5_3.validate(data)
        kcidb_io.schema.V5_3.upgrade(data)

        processing_time = time.time() - start_time
        return data, {
            "file": file,
            "fsize": fsize,
            "processing_time": processing_time,
        }
    except Exception as e:
        logger.error("Error preparing data from %s: %s", file.name, e)
        logger.error(traceback.format_exc())
        return None, {
            "file": file,
            "error": str(e),
        }


def db_worker(stop_event: threading.Event) -> None:  # noqa: C901
    """
    Worker thread that processes the database queue.
    This is the only thread that interacts with the database.

    Args:
        stop_event: threading.Event (flag) to signal the worker to stop processing
    """

    # Local buffers for batching
    issues_buf = []
    checkouts_buf = []
    builds_buf = []
    tests_buf = []
    incidents_buf = []

    last_flush_ts = time.time()

    def buffered_total():
        return (
            len(issues_buf)
            + len(checkouts_buf)
            + len(builds_buf)
            + len(tests_buf)
            + len(incidents_buf)
        )

    def flush_buffers():
        nonlocal last_flush_ts
        total = buffered_total()
        if total == 0:
            return

        # Insert in dependency-safe order
        flush_start = time.time()
        try:
            # Single transaction for all tables in the flush
            with transaction.atomic():
                if issues_buf:
                    t0 = time.time()
                    Issues.objects.bulk_create(
                        issues_buf, batch_size=INGEST_BATCH_SIZE, ignore_conflicts=True
                    )
                    _out(
                        "bulk_create issues: n=%d in %.3fs"
                        % (len(issues_buf), time.time() - t0)
                    )
                if checkouts_buf:
                    t0 = time.time()
                    Checkouts.objects.bulk_create(
                        checkouts_buf,
                        batch_size=INGEST_BATCH_SIZE,
                        ignore_conflicts=True,
                    )
                    _out(
                        "bulk_create checkouts: n=%d in %.3fs"
                        % (len(checkouts_buf), time.time() - t0)
                    )
                if builds_buf:
                    t0 = time.time()
                    Builds.objects.bulk_create(
                        builds_buf, batch_size=INGEST_BATCH_SIZE, ignore_conflicts=True
                    )
                    _out(
                        "bulk_create builds: n=%d in %.3fs"
                        % (len(builds_buf), time.time() - t0)
                    )
                if tests_buf:
                    t0 = time.time()
                    Tests.objects.bulk_create(
                        tests_buf, batch_size=INGEST_BATCH_SIZE, ignore_conflicts=True
                    )
                    _out(
                        "bulk_create tests: n=%d in %.3fs"
                        % (len(tests_buf), time.time() - t0)
                    )
                if incidents_buf:
                    t0 = time.time()
                    Incidents.objects.bulk_create(
                        incidents_buf,
                        batch_size=INGEST_BATCH_SIZE,
                        ignore_conflicts=True,
                    )
                    _out(
                        "bulk_create incidents: n=%d in %.3fs"
                        % (len(incidents_buf), time.time() - t0)
                    )
        except Exception as e:
            logger.error("Error during bulk_create flush: %s", e)
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
            _out(msg)
            issues_buf.clear()
            checkouts_buf.clear()
            builds_buf.clear()
            tests_buf.clear()
            incidents_buf.clear()
            last_flush_ts = time.time()

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
                    flush_buffers()

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
                    _out(msg)
            except Exception as e:
                logger.error("Error processing item in db_worker: %s", e)
            finally:
                db_queue.task_done()

        except Empty:
            # Time-based flush when idle
            if (time.time() - last_flush_ts) >= INGEST_FLUSH_TIMEOUT_SEC:
                if VERBOSE:
                    _out(
                        "Idle flush after %.1fs without new items (buffered=%d)"
                        % (
                            INGEST_FLUSH_TIMEOUT_SEC,
                            buffered_total(),
                        )
                    )
                flush_buffers()
            continue
        except Exception as e:
            logger.error("Unexpected error in db_worker: %s", e)

    # Final flush after loop ends
    flush_buffers()


def process_file(
    file: DirEntry[str],
    tree_names: dict[str, str],
    failed_dir: str,
    archive_dir: str,
) -> bool:
    """
    Process a single file in a thread, then queue it for database insertion.
    """
    data, metadata = prepare_file_data(file, tree_names)
    file = metadata["file"]

    if "error" in metadata:
        try:
            move_file_to_failed_dir(os.path.join(file.path, file.name), failed_dir)
        except Exception:
            pass
        return False

    if data is None:
        # Empty file, already deleted
        return True

    db_queue.put((file.name, build_instances_from_submission(data)))

    # Archive the file after queuing (we can do this optimistically)
    try:
        os.rename(file.path, os.path.join(archive_dir, file.name))
    except Exception as e:
        logger.error("Error archiving file %s: %s", file.name, e)
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

    _out(
        "Spool status: %d .json files queued (%.2f MB)"
        % (
            len(json_files),
            total_bytes / (1024 * 1024) if total_bytes else 0.0,
        )
    )

    cycle_start = time.time()
    total_files_count = len(json_files)

    # Start database worker thread
    # This thread will constantly consume the db_queue and send data to the database
    stop_event = threading.Event()
    db_thread = threading.Thread(target=db_worker, args=(stop_event,))
    db_thread.start()

    stat_ok = 0
    stat_fail = 0

    processed = 0
    last_progress = cycle_start
    progress_every_n = 200
    progress_every_sec = 2.0

    try:
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all files for processing
            future_to_file = {
                executor.submit(
                    process_file, file, tree_names, failed_dir, archive_dir
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
                        _out(msg)
                        last_progress = now

        _out("Waiting for DB queue to drain... size=%d" % db_queue.qsize())
        # Wait for all database operations to complete
        db_queue.join()

    except KeyboardInterrupt:
        _out("KeyboardInterrupt: stopping ingestion and flushing...")
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
        db_thread.join()

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
        _out(msg)
    else:
        _out("No files processed, nothing to do")


def verify_dir(dir: str) -> None:
    if not os.path.exists(dir):
        logger.error("Directory %s does not exist", dir)
        # try to create it
        try:
            os.makedirs(dir)
            logger.info("Directory %s created", dir)
        except Exception as e:
            logger.error("Error creating directory %s: %s", dir, e)
            raise e
    if not os.path.isdir(dir):
        raise Exception(f"Directory {dir} is not a directory")
    if not os.access(dir, os.W_OK):
        raise Exception(f"Directory {dir} is not writable")
    logger.info("Directory %s is valid and writable", dir)


def verify_spool_dirs(spool_dir: str) -> None:
    failed_dir = os.path.join(spool_dir, "failed")
    archive_dir = os.path.join(spool_dir, "archive")
    verify_dir(spool_dir)
    verify_dir(failed_dir)
    verify_dir(archive_dir)


def cache_logs_maintenance() -> None:
    """
    Periodically clean up the cache logs to prevent memory leak and slow down.
    If CACHE_LOGS grow over 100k entries, clear it.
    """

    # Limit the size of the cache to prevent memory leaks
    # (we don't really need lock, as workers idle, but just in case)
    with cache_logs_lock:
        if len(CACHE_LOGS) > CACHE_LOGS_SIZE_LIMIT:
            CACHE_LOGS.clear()
            if VERBOSE:
                logger.info("Cache logs cleared")
