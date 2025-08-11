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

import kcidb
import tempfile
import os
import argparse
from kcidb import io, db, mq, orm, oo, monitor, tests, unittest, misc # noqa
import json
import time
import logging
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
import functools
import requests
import hashlib
import tempfile
import threading
from queue import Queue
import queue
import traceback
import gzip

# default database
DATABASE = "postgresql:dbname=kcidb user=kcidb password=kcidb host=localhost port=5432"
VERBOSE = 0
STORAGE_TOKEN = os.environ.get("STORAGE_TOKEN", None)
STORAGE_BASE_URL = os.environ.get("STORAGE_BASE_URL", None)
LOGEXCERPT_THRESHOLD = 256  # 256 bytes threshold for logexcerpt
CONVERT_LOG_EXCERPT = False  # If True, convert log_excerpt to output_files url
CACHE_LOGS = {}
cache_logs_lock = threading.Lock()

logger = logging.getLogger('ingester')

# Thread-safe queue for database operations
db_queue = Queue()
db_lock = threading.Lock()

def get_db_credentials():
    global DATABASE
    # if PG_URI present - use it instead of default DATABASE
    pg_uri = os.environ.get("PG_URI")
    if pg_uri:
        DATABASE = pg_uri
    pgpass = os.environ.get("POSTGRES_PASSWORD")
    if not pgpass:
        raise Exception("POSTGRES_PASSWORD environment variable not set")
    (pgpass_fd, pgpass_filename) = tempfile.mkstemp(suffix=".pgpass")
    with os.fdopen(pgpass_fd, mode="w", encoding="utf-8") as pgpass_file:
        pgpass_file.write(pgpass)
    os.environ["PGPASSFILE"] = pgpass_filename
    db_uri = os.environ.get("PG_DSN")
    if db_uri:
        DATABASE = db_uri


def get_db_client(database):
    get_db_credentials()
    db = kcidb.db.Client(database)
    return db


def move_file_to_failed_dir(filename, failed_dir):
    try:
        os.rename(filename, os.path.join(failed_dir, os.path.basename(filename)))
    except Exception as e:
        print(f"Error moving file {filename} to failed directory: {e}")
        raise e

TREES_FILE = "/app/trees.yml"

def load_trees_name():
    with open(TREES_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    trees_name = {
        v["url"]: tree_name
        for tree_name, v in data.get("trees", {}).items()
    }

    return trees_name


def standardize_trees_name(input_data, trees_name):
    """ Standardize tree names in input data using the provided mapping """

    for checkout in input_data.get("checkouts", []):
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
        # gzip the logexcerpt
        logexcerpt_compressed = gzip.compress(logexcerpt.encode('utf-8'))
        # write to the temporary file
        temp_file.write(logexcerpt_compressed)
        temp_file.flush()
    with open(logexcerpt_filename, "rb") as f:
        hdr = {
            "Authorization": f"Bearer {STORAGE_TOKEN}",
        }
        files={
            "file0": ("logexcerpt.txt.gz", f),
            "path": f"logexcerpt/{id}"
        }
        try:
            r = requests.post(
                upload_url,
                headers=hdr,
                files=files
            )
        except Exception as e:
            logger.error(f"Error uploading logexcerpt for {id}: {e}")
            os.remove(logexcerpt_filename)
            return logexcerpt  # Return original logexcerpt if upload fails
    os.remove(logexcerpt_filename)
    if r.status_code != 200:
        logger.error(f"Failed to upload logexcerpt for {id}: {r.status_code} : {r.text}")
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
    global CACHE_LOGS
    with cache_logs_lock:
        CACHE_LOGS[log_hash] = url
        if VERBOSE:
            logger.info(f"Cached log excerpt with hash {log_hash} at {url}")


def set_log_excerpt_ofile(build, url):
    """
    Clean log_excerpt field
    Create name/url dict and append to output_files of job
    """
    build["log_excerpt"] = ""
    data = {
        "name": "log_excerpt",
        "url": url,
    }
    if "output_files" not in build:
        build["output_files"] = []
    
    build["output_files"].append(data)
    return build


def extract_log_excerpt(input_data):
    """
    Extract log_excerpt from builds and tests, if it is large,
    upload to storage and replace with a reference
    """
    if not STORAGE_TOKEN or not STORAGE_BASE_URL:
        logger.warning("STORAGE_TOKEN or STORAGE_BASE_URL "
                       "is not set, log_excerpts will not be uploaded")
        return input_data

    builds = input_data.get("builds", [])
    tests = input_data.get("tests", [])
    for build in builds:
        if build.get("log_excerpt"):
            id = build.get("id", "unknown")
            log_excerpt = build["log_excerpt"]
            if isinstance(log_excerpt, str) and len(log_excerpt) > LOGEXCERPT_THRESHOLD:
                log_hash = hashlib.sha256(log_excerpt.encode('utf-8')).hexdigest()
                if VERBOSE:
                    logger.info(f"Uploading log_excerpt for build {id} hash {log_hash} with size {len(log_excerpt)} bytes")
                cached_url = get_from_cache(log_hash)
                if cached_url:
                    if VERBOSE:
                        logger.info(f"Log excerpt for build {id} already uploaded, using cached URL")
                    set_log_excerpt_ofile(build, cached_url)
                else:
                    cached_url = upload_logexcerpt(log_excerpt, log_hash)
                    set_in_cache(log_hash, cached_url)
                    set_log_excerpt_ofile(build, cached_url)

    for test in tests:
        if test.get("log_excerpt"):
            id = test.get("id", "unknown")
            log_excerpt = test["log_excerpt"]
            if isinstance(log_excerpt, str) and len(log_excerpt) > LOGEXCERPT_THRESHOLD:
                log_hash = hashlib.sha256(log_excerpt.encode('utf-8')).hexdigest()
                if VERBOSE:
                    logger.info(f"Uploading log_excerpt for test {id} hash {log_hash} with size {len(log_excerpt)} bytes")
                # check if log_excerpt already uploaded (by hash as key)
                cached_url = get_from_cache(log_hash)
                if cached_url:
                    if VERBOSE:
                        logger.info(f"Log excerpt for test {id} already uploaded, using cached URL")
                    set_log_excerpt_ofile(test, cached_url)
                else:
                    cached_url = upload_logexcerpt(log_excerpt, log_hash)
                    set_in_cache(log_hash, cached_url)
                    set_log_excerpt_ofile(test, cached_url)

    return input_data


def prepare_file_data(filename, trees_name, spool_dir, io_schema):
    """
    Prepare file data: read, extract log excerpts, standardize tree names, validate.
    This function does everything except the actual database load.
    """
    full_filename = os.path.join(spool_dir, filename)
    fsize = os.path.getsize(full_filename)
    
    if fsize == 0:
        if VERBOSE:
            logger.info(f"File {full_filename} is empty, skipping, deleting")
        os.remove(full_filename)
        return None, None
    
    start_time = time.time()
    if VERBOSE:
        logger.info(f"Processing file {filename}, size: {fsize}")
    
    try:
        with open(full_filename, "r") as f:
            data = json.loads(f.read())
        
        # These operations can be done in parallel (especially extract_log_excerpt)
        if CONVERT_LOG_EXCERPT:
            data = extract_log_excerpt(data)
        data = standardize_trees_name(data, trees_name)
        data = io_schema.validate(data)
        data = io_schema.upgrade(data, copy=False)
        
        processing_time = time.time() - start_time
        return data, {
            'filename': filename,
            'full_filename': full_filename,
            'fsize': fsize,
            'processing_time': processing_time
        }
    except Exception as e:
        logger.error(f"Error preparing data from {filename}: {e}")
        logger.error(traceback.format_exc())
        return None, {
            'filename': filename,
            'full_filename': full_filename,
            'error': str(e)
        }


def db_worker(db_client, stop_event):
    """
    Worker thread that processes the database queue.
    This is the only thread that interacts with the database.
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
                        db_client.load(data)
                    
                    if VERBOSE and 'processing_time' in metadata:
                        ing_speed = metadata['fsize'] / metadata['processing_time'] / 1024
                        logger.info(f"Ingested {metadata['filename']} in {ing_speed:.2f} KB/s")
                if VERBOSE:
                    logger.info(f"Processed file {metadata['filename']} with size {metadata['fsize']} bytes")
            except Exception as e:
                logger.error(f"Error processing item in db_worker: {e}")
            finally:
                db_queue.task_done()  # Always mark task as done, even if processing failed
                
        except queue.Empty:
            continue  # Timeout occurred, continue to check stop_event
        except Exception as e:
            logger.error(f"Unexpected error in db_worker: {e}")


def process_file(filename, trees_name, spool_dir, io_schema):
    """
    Process a single file in a thread, then queue it for database insertion.
    """
    failed_dir = os.path.join(spool_dir, "failed")
    archive_dir = os.path.join(spool_dir, "archive")
    
    data, metadata = prepare_file_data(filename, trees_name, spool_dir, io_schema)
    
    if 'error' in metadata:
        # Move to failed directory
        try:
            move_file_to_failed_dir(metadata['full_filename'], failed_dir)
        except:
            pass
        return False
    
    if data is None:
        # Empty file, already deleted
        return True
    
    # Queue for database insertion
    db_queue.put((data, metadata))
    
    # Archive the file after queuing (we can do this optimistically)
    try:
        os.rename(metadata['full_filename'], os.path.join(archive_dir, metadata['filename']))
    except Exception as e:
        logger.error(f"Error archiving file {metadata['filename']}: {e}")
        return False
    
    return True


def ingest_submissions_parallel(spool_dir, trees_name, db_client=None, max_workers=5):
    """
    Ingest submissions in parallel using ThreadPoolExecutor for I/O operations
    and a single database worker thread.
    """
    if db_client is None:
        raise Exception("db_client is None")
    
    io_schema = db_client.get_schema()[1]
    
    # Get list of JSON files to process
    json_files = [
        f for f in os.listdir(spool_dir)
        if os.path.isfile(os.path.join(spool_dir, f)) and f.endswith(".json")
    ]
    
    if not json_files:
        return
    
    logger.info(f"Found {len(json_files)} files to process")
    
    # Start database worker thread
    stop_event = threading.Event()
    db_thread = threading.Thread(target=db_worker, args=(db_client, stop_event))
    db_thread.start()
    
    stat_ok = 0
    stat_fail = 0
    
    try:
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all files for processing
            future_to_file = {
                executor.submit(process_file, filename, trees_name, spool_dir, io_schema): filename
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
        logger.info(f"Processed {stat_ok + stat_fail} files: {stat_ok} succeeded, {stat_fail} failed")
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
    If CACHE_LOGS grow over 100k entries, truncate it to 0.
    """
    global CACHE_LOGS

    # Limit the size of the cache to prevent memory leaks
    # (we don't really need lock, as workers idle, but just in case)
    with cache_logs_lock:
        if len(CACHE_LOGS) > 100000:  # Arbitrary limit, adjust as needed
            CACHE_LOGS.clear()
            if VERBOSE:
                logger.info("Cache logs cleared")


def main():
    global VERBOSE, CONVERT_LOG_EXCERPT
    # read from environment variable KCIDB_VERBOSE
    VERBOSE = int(os.environ.get("KCIDB_VERBOSE", 0))
    if VERBOSE:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    CONVERT_LOG_EXCERPT = os.environ.get("CONVERT_LOG_EXCERPT", "False").lower() in ("true", "1", "yes")

    parser = argparse.ArgumentParser()
    parser.add_argument("--spool-dir", type=str, required=True)
    parser.add_argument("--verbose", type=int, default=VERBOSE)
    parser.add_argument("--max-workers", type=int, default=5, 
                        help="Maximum number of parallel workers for file processing")
    args = parser.parse_args()
    
    VERBOSE = args.verbose
    
    logger.info("Starting ingestion process...")
    verify_spool_dirs(args.spool_dir)
    trees_name = load_trees_name()
    get_db_credentials()
    db_client = get_db_client(DATABASE)
    
    while True:
        ingest_submissions_parallel(args.spool_dir, trees_name, db_client, args.max_workers)
        cache_logs_maintenance()
        time.sleep(1)


if __name__ == "__main__":
    main()