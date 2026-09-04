# Ingester

The ingester is a Django management command that reads KCIDB submission
JSON files from a spool directory and writes them into the PostgreSQL
database. It runs as a long-lived process on `db.kernelci.org`.

Entry point: `backend/kernelCI_app/management/commands/helpers/kcidbng_ingester.py`

## Parallel ingestion

`ingest_submissions_parallel()` is the main orchestration function.
It uses `multiprocessing.Process` workers and a shared
`multiprocessing.Queue` to parallelize file parsing and database writes.

### Data flow

```
json_files (list)
    |
    v
[batch into groups of INGEST_FILES_BATCH_SIZE]
    |
    v
multiprocessing.Queue (maxsize = INGEST_QUEUE_MAXSIZE)
    |                       |               |
    v                       v               v
  worker 0              worker 1    ...   worker N-1
  (process_batch)       (process_batch)   (process_batch)
    |                       |               |
    v                       v               v
  DB writes via         DB writes via     DB writes via
  flush_buffers()       flush_buffers()   flush_buffers()
```

### Worker-queue protocol

1. **Spool phase** - The main process batches `json_files` into groups
   of `INGEST_FILES_BATCH_SIZE` and puts each batch into the queue.
   This happens before any workers start.

2. **Start workers** - `max_workers` child processes are spawned. Each
   runs `process_batch()`, which loops on `process_queue.get()` until
   it receives `None`.

3. **Enqueue poison pills** - One `None` per worker is put into the
   queue alongside worker starts. Since batches are already in the
   queue (FIFO), the Nones always sit behind all batches and workers
   consume them only after all real work is done.

4. **Wait for completion** - The main loop waits for the queue to
   drain, reporting progress every `progress_every_sec` seconds. If
   all workers exit while items remain in the queue, the loop logs an
   error and breaks instead of hanging indefinitely.

5. **Join** - After all workers exit, the main process joins them and
   prints a final progress report.

### Worker internals (process_batch)

Each worker:

- Closes inherited DB connections (`connections.close_all()`) and opens
  fresh ones, since connections cannot be shared across processes.
- Accumulates parsed instances (issues, checkouts, builds, tests,
  incidents) into an in-memory buffer.
- Flushes the buffer to the database via `flush_buffers()` whenever
  any entity type reaches `INGEST_BATCH_SIZE`.
- Sorts instances by ID before flushing to prevent deadlocks when
  multiple workers update the same rows concurrently.
- On exit (receiving `None`), flushes any remaining buffered instances.

### Error handling

- **File parse errors**: The file is moved to the `failed` directory
  and the `stat_fail` counter is incremented. The worker continues
  processing subsequent files.
- **Worker crash**: `is_alive()` returns False, so the main loop
  breaks and joins the remaining workers. After join, non-zero exit
  codes are logged and the `kcidb_ingester_worker_failures` counter
  is incremented with `reason="exception"` (positive exit code) or
  `reason="signal"` (negative, e.g. SIGKILL/-9 from OOM killer).
- **Worker hang**: Depends on `requests` timeouts (set on all
  production HTTP calls) to eventually unblock the worker.
- **KeyboardInterrupt**: The main process terminates all live workers
  and joins them.

### Log excerpts

When `CONVERT_LOG_EXCERPT` is enabled and `STORAGE_TOKEN` is set,
large log excerpts (exceeding `LOGEXCERPT_THRESHOLD` bytes) are
compressed with gzip and uploaded to external storage. The log excerpt
field is then replaced with a URL reference. An in-memory cache
(`CACHE_LOGS`) deduplicates uploads by SHA-256 hash.

See: `backend/kernelCI_app/management/commands/helpers/log_excerpt_utils.py`

### Relevant constants

Defined in `backend/kernelCI_app/constants/ingester.py`:

- `INGEST_FILES_BATCH_SIZE` - Number of files per queue batch
- `INGEST_BATCH_SIZE` - Number of DB instances before flushing
- `INGEST_QUEUE_MAXSIZE` - Bounded queue size (backpressure)
- `LOGEXCERPT_THRESHOLD` - Byte threshold for uploading log excerpts

Defined in `backend/kernelCI_app/constants/general.py`:

- `REQUESTS_TIMEOUT_UPLOAD_IN_SECONDS` (30s) - Timeout for log excerpt uploads to storage
- `REQUESTS_TIMEOUT_WEBHOOK_IN_SECONDS` (10s) - Timeout for Discord webhook posts
- `REQUESTS_TIMEOUT_FETCH_IN_SECONDS` (30s) - Timeout for fetching external log pages
