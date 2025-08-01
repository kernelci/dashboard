# SPDX-License-Identifier: LGPL-2.1-only
# Copyright (C) 2025 Collabora Ltd
# Author: Denys Fedoryshchenko <denys.f@collabora.com>
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; version 2.1.
#
# This library is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
import hashlib
import json
import jsonschema
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

from kernelCI_ingester.helpers.schema_versions.current_schema import CurrentSchema
from kernelCI_ingester.management.commands.helpers.process_submissions import (
    process_submission_data,
)

VERBOSE = 0
LOGEXCERPT_THRESHOLD = 256  # 256 bytes threshold for logexcerpt
CONVERT_LOG_EXCERPT = False  # If True, convert log_excerpt to output_files url

CACHE_LOGS = {}
CACHE_LOGS_SIZE_LIMIT = 100000  # Arbitrary limit for cache_logs size, adjust as needed
cache_logs_lock = threading.Lock()

STORAGE_TOKEN = os.environ.get("STORAGE_TOKEN", None)
STORAGE_BASE_URL = "https://files-staging.kernelci.org"

TREES_FILE = "/app/trees.yaml"

logger = logging.getLogger("ingester")

# Thread-safe queue for database operations
db_queue = Queue()
db_lock = threading.Lock()


def verbose_info(msg: str):
    """
    Log a message at the INFO level if VERBOSE is enabled.

    This function is mainly used to avoid repetitive checks for the VERBOSE flag,
    in order to lower the other functions' complexity.
    """
    if VERBOSE:
        logger.info(msg)


def move_file_to_failed_dir(filename, failed_dir):
    try:
        os.rename(filename, os.path.join(failed_dir, os.path.basename(filename)))
    except Exception as e:
        logger.error(f"Error moving file {filename} to failed directory: {e}")
        raise e


def load_trees_name(trees_file_override: Optional[str]) -> dict[str, str]:
    global TREES_FILE
    if trees_file_override is not None:
        TREES_FILE = trees_file_override

    with open(TREES_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    trees_name = {v["url"]: tree_name for tree_name, v in data.get("trees", {}).items()}

    return trees_name


def standardize_trees_name(input_data: dict[str, Any], trees_name):
    """
    Standardize tree names in input data using the provided mapping

    Returns the modified input data with standardized tree names.
    """

    checkouts: list[dict[str, Any]] = input_data.get("checkouts", [])

    for checkout in checkouts:
        git_url = checkout.get("git_repository_url")
        if git_url in trees_name:
            correct_tree = trees_name[git_url]
            if checkout.get("tree_name") != correct_tree:
                checkout["tree_name"] = correct_tree

    return input_data


def upload_logexcerpt(logexcerpt, id):
    """
    Upload logexcerpt to storage and return a reference(URL)
    """
    upload_url = f"{STORAGE_BASE_URL}/upload"
    if VERBOSE:
        logger.info(f"Uploading logexcerpt for {id} to {upload_url}")
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
            logger.error(f"Error uploading logexcerpt for {id}: {e}")
            os.remove(logexcerpt_filename)
            return logexcerpt  # Return original logexcerpt if upload fails
    os.remove(logexcerpt_filename)
    if r.status_code != 200:
        logger.error(
            f"Failed to upload logexcerpt for {id}: {r.status_code} : {r.text}"
        )
        return logexcerpt  # Return original logexcerpt if upload fails

    return f"{STORAGE_BASE_URL}/logexcerpt/{id}/logexcerpt.txt.gz"


def get_from_cache(log_hash):
    """
    Check if log_hash is in the cache
    """
    with cache_logs_lock:
        return CACHE_LOGS.get(log_hash)


def set_in_cache(log_hash, url):
    """
    Set log_hash in the cache with the given URL
    """
    with cache_logs_lock:
        CACHE_LOGS[log_hash] = url
        if VERBOSE:
            logger.info(f"Cached log excerpt with hash {log_hash} at {url}")


def set_log_excerpt_ofile(item: dict[str, Any], url):
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
    item: dict[str, Any], type: Literal["build", "test"]
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
                f"Uploading log_excerpt for {type} id {id} hash {log_hash} with size {len(log_excerpt)} bytes"
            )
        # check if log_excerpt already uploaded (by hash as key)
        cached_url = get_from_cache(log_hash)
        if cached_url:
            if VERBOSE:
                logger.info(
                    f"Log excerpt for {type} {id} already uploaded, using cached URL"
                )
            set_log_excerpt_ofile(item, cached_url)
        else:
            cached_url = upload_logexcerpt(log_excerpt, log_hash)
            set_in_cache(log_hash, cached_url)
            set_log_excerpt_ofile(item, cached_url)


def extract_log_excerpt(input_data: dict[str, Any]) -> dict[str, Any]:
    """
    Extract log_excerpt from builds and tests, if it is large,
    upload to storage and replace with a reference.

    Returns:
        input_data: dict with log_excerpt replaced by URL if it was large
    """
    if not STORAGE_TOKEN:
        logger.warning("STORAGE_TOKEN is not set, log_excerpts will not be uploaded")
        return input_data

    builds: list[dict[str, Any]] = input_data.get("builds", [])
    tests: list[dict[str, Any]] = input_data.get("tests", [])

    for build in builds:
        if build.get("log_excerpt"):
            process_log_excerpt_from_item(item=build, type="build")

    for test in tests:
        if test.get("log_excerpt"):
            process_log_excerpt_from_item(item=test, type="test")

    return input_data


def validate_data_schema(
    data: dict[str, Any], full_filename: Optional[str] = None
) -> None:
    """
    Validate submission data against the JSON schema.

    Args:
        data: The submission data to validate
        full_filename: The filename of the data currently being validated. Used only for error report.
    """
    try:
        schema = CurrentSchema()
        schema.validate(data)

        print(
            f"Schema validation passed for submission with version {data.get('version', 'unknown')}"
        )

    except jsonschema.ValidationError as e:
        if full_filename:
            error_msg = f"Schema validation failed at {full_filename}"
        else:
            error_msg = "Schema validation failed at unknown file"
        logger.error(error_msg)
        raise e

    except jsonschema.SchemaError as e:
        logger.error(f"Schema itself is invalid: {e.message}")
        raise e

    except Exception as e:
        logger.error(f"Unexpected error during schema validation: {str(e)}")
        raise e


def prepare_file_data(filename, trees_name, spool_dir):
    """
    Prepare file data: read, extract log excerpts, standardize tree names, validate.
    This function does everything except the actual database load.
    """
    full_filename = os.path.join(spool_dir, filename)
    fsize = os.path.getsize(full_filename)

    if fsize == 0:
        verbose_info(f"File {full_filename} is empty, skipping, deleting")
        os.remove(full_filename)
        return None, None

    start_time = time.time()
    verbose_info(f"Processing file {filename}, size: {fsize}")

    try:
        with open(full_filename, "r") as f:
            data = json.loads(f.read())

        # These operations can be done in parallel (especially extract_log_excerpt)
        if CONVERT_LOG_EXCERPT:
            data = extract_log_excerpt(data)
        data = standardize_trees_name(data, trees_name)
        validate_data_schema(data, full_filename)

        processing_time = time.time() - start_time
        return data, {
            "filename": filename,
            "full_filename": full_filename,
            "fsize": fsize,
            "processing_time": processing_time,
        }
    except Exception as e:
        logger.error(f"Error preparing data from {filename}: {e}")
        logger.error(traceback.format_exc())
        return None, {
            "filename": filename,
            "full_filename": full_filename,
            "error": str(e),
        }


def db_worker(stop_event: threading.Event):
    """
    Worker thread that processes the database queue.
    This is the only thread that interacts with the database.

    Params:
        stop_event: threading.Event (flag) to signal the worker to stop processing
    """

    while not stop_event.is_set() or not db_queue.empty():
        try:
            item = db_queue.get(timeout=0.1)
            if item is None:
                db_queue.task_done()  # Important: mark the poison pill as done
                break
            try:
                data, metadata = item
                if data is not None:
                    with db_lock:
                        # TODO: Replace with actual DB insert function
                        process_submission_data(data, metadata)

                    if VERBOSE and "processing_time" in metadata:
                        ing_speed = (
                            metadata["fsize"] / metadata["processing_time"] / 1024
                        )
                        logger.info(
                            f"Ingested {metadata['filename']} in {ing_speed:.2f} KB/s"
                        )
                verbose_info(
                    f"Processed file {metadata['filename']} with size {metadata['fsize']} bytes"
                )
            except Exception as e:
                logger.error(f"Error processing item in db_worker: {e}")
            finally:
                db_queue.task_done()  # Always mark task as done, even if processing failed

        except Empty:
            continue  # Timeout occurred, continue to check stop_event
        except Exception as e:
            logger.error(f"Unexpected error in db_worker: {e}")


def process_file(filename, trees_name, spool_dir):
    """
    Process a single file in a thread, then queue it for database insertion.
    """
    failed_dir = os.path.join(spool_dir, "failed")
    archive_dir = os.path.join(spool_dir, "archive")

    data, metadata = prepare_file_data(filename, trees_name, spool_dir)

    if "error" in metadata:
        try:
            move_file_to_failed_dir(metadata["full_filename"], failed_dir)
        except Exception:
            pass
        return False

    if data is None:
        # Empty file, already deleted
        return True

    db_queue.put((data, metadata))

    # Archive the file after queuing (we can do this optimistically)
    try:
        os.rename(
            metadata["full_filename"], os.path.join(archive_dir, metadata["filename"])
        )
    except Exception as e:
        logger.error(f"Error archiving file {metadata['filename']}: {e}")
        return False

    return True


def ingest_submissions_parallel(
    spool_dir: str, trees_name: dict[str, str], max_workers=5
):
    """
    Ingest submissions in parallel using ThreadPoolExecutor for I/O operations
    and a single database worker thread.
    """

    # Get list of JSON files to process
    json_files = [
        f
        for f in os.listdir(spool_dir)
        if os.path.isfile(os.path.join(spool_dir, f)) and f.endswith(".json")
    ]
    if not json_files:
        return

    logger.info(f"Found {len(json_files)} files to process")

    # Start database worker thread
    # This thread will constantly consume the db_queue and send data to the database
    stop_event = threading.Event()
    db_thread = threading.Thread(target=db_worker, args=(stop_event,))
    db_thread.start()

    stat_ok = 0
    stat_fail = 0

    try:
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all files for processing
            future_to_file = {
                executor.submit(process_file, filename, trees_name, spool_dir): filename
                for filename in json_files
            }

            # Collect results
            for future in as_completed(future_to_file):
                filename = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        stat_ok += 1
                    else:
                        stat_fail += 1
                except Exception as e:
                    logger.error(f"Exception processing {filename}: {e}")
                    stat_fail += 1

        # Wait for all database operations to complete
        db_queue.join()

    finally:
        # Signal database worker to stop
        stop_event.set()
        db_queue.put(None)  # Poison pill
        db_thread.join()

    if stat_ok + stat_fail > 0:
        logger.info(
            f"Processed {stat_ok + stat_fail} files: {stat_ok} succeeded, {stat_fail} failed"
        )
    else:
        logger.info("No files processed, nothing to do")


def verify_dir(dir):
    if not os.path.exists(dir):
        logger.error(f"Directory {dir} does not exist")
        # try to create it
        try:
            os.makedirs(dir)
            logger.info(f"Directory {dir} created")
        except Exception as e:
            logger.error(f"Error creating directory {dir}: {e}")
            raise e
    if not os.path.isdir(dir):
        raise Exception(f"Directory {dir} is not a directory")
    if not os.access(dir, os.W_OK):
        raise Exception(f"Directory {dir} is not writable")
    logger.info(f"Directory {dir} is valid and writable")


def verify_spool_dirs(spool_dir):
    failed_dir = os.path.join(spool_dir, "failed")
    archive_dir = os.path.join(spool_dir, "archive")
    verify_dir(spool_dir)
    verify_dir(failed_dir)
    verify_dir(archive_dir)


def cache_logs_maintenance():
    """
    Periodically clean up the cache logs to prevent memory leak and slow down.
    If CACHE_LOGS grow over 100k entries, clear it.
    """

    # Limit the size of the cache to prevent memory leaks
    # (we don't really need lock, as workers idle, but just in case)
    with cache_logs_lock:
        if len(CACHE_LOGS) > CACHE_LOGS_SIZE_LIMIT:
            CACHE_LOGS.clear()
            verbose_info("Cache logs cleared")
