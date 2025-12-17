import gzip
import hashlib
import logging
import os
import requests
import tempfile
import threading
from typing import Any, Literal, Optional
from kernelCI_app.constants.ingester import (
    CACHE_LOGS_SIZE_LIMIT,
    LOGEXCERPT_THRESHOLD,
    STORAGE_TOKEN,
    STORAGE_BASE_URL,
    UPLOAD_URL,
    VERBOSE,
)


CACHE_LOGS = {}
cache_logs_lock = threading.Lock()
logger = logging.getLogger("ingester")


def upload_logexcerpt(logexcerpt: str, id: str) -> str:
    """
    Upload logexcerpt to storage and return a reference (URL string) if successful.
    If fails, returns the original logexcerpt.

    Args:
        logexcerpt: the unchanged logexcerpt
        id: the hash of the logexcerpt

    Returns:
        str: On success upload: the reference url. On failed upload: the original logexcerpt
    """
    if VERBOSE:
        logger.info("Uploading logexcerpt for %s to %s", id, UPLOAD_URL)
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
            r = requests.post(UPLOAD_URL, headers=hdr, files=files)
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

    Returns:
        str|None: The log_excerpt if it exists in cache, None otherwise
    """
    with cache_logs_lock:
        return CACHE_LOGS.get(log_hash)


def set_in_cache(log_hash: str, log_excerpt: str) -> None:
    """
    Set log_hash in the cache with the given log_excerpt.
    Ideally, the log_excerpt will arrive as a reference URL to where it was stored.
    It can arrive as the entire log_excerpt though.
    """
    with cache_logs_lock:
        CACHE_LOGS[log_hash] = log_excerpt
        if VERBOSE:
            logger.info("Cached log excerpt with hash %s as %s", log_hash, log_excerpt)


def set_log_excerpt_ofile(item: dict[str, Any], url: str) -> dict[str, Any]:
    """
    Clean log_excerpt field
    Create name/url dict and append to output_files of job

    item is a build or test
    """
    item["log_excerpt"] = ""
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
            # TODO: if upload_logexcerpt fails, should we be caching the entire logexcerpt?
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
