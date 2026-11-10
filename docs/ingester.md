# Ingester

The ingester is a Django management command that reads KCIDB submission
JSON files from a spool directory and writes them into the PostgreSQL
database. It runs as a long-lived process on `db.kernelci.org`.

Entry point: `backend/kernelCI_app/management/commands/helpers/kcidbng_ingester.py`

## Parallel ingestion

`monitor_submissions` keeps one `IngestionWorkers` context alive for the
command's lifetime. It starts `max_workers` processes once, using `fork`, and
feeds them through a bounded shared queue. The one-shot
`ingest_submissions_parallel()` entry point remains available for benchmarks.

### Worker-queue protocol

1. The parent sends each worker a start message through its control pipe.
2. It queues file batches, including the final partial batch, followed by one
   end-of-cycle sentinel per worker. Workers are already running, so a full
   queue applies backpressure without preventing them from starting.
3. Each worker processes batches, consumes one sentinel, flushes its remaining
   buffers, closes its database connections, and acknowledges completion.
4. The worker waits on its control pipe until the next cycle. It cannot consume
   another worker's sentinel. The parent waits for every acknowledgement before
   resetting counters or starting another cycle.
5. On normal shutdown the parent sends stop messages and joins the workers.
   On an exception it kills them, since workers ignore SIGTERM (see below).

Workers poll the queue with a timeout. A worker whose parent died mid-cycle
would otherwise wait forever for a sentinel; instead it flushes what it has
buffered and exits.

### Metrics accumulation

Persistent workers stop the per-cycle creation of Prometheus metric files.
`kcidb_ingester_prometheus_files{ingester="django"}` reports the number of `.db`
files in `PROMETHEUS_MULTIPROC_DIR`. The monitor samples it at most once per minute,
between ingestion cycles; a long cycle delays the next update. The count should
settle after workers have exercised their metrics and then remain stable.

Worker cleanup calls `mark_process_dead()` after joining each process. This
removes live-gauge files while retaining counter and histogram totals. The
existing startup cleanup clears the directory when the command restarts.

For an accumulation check, record the file-count gauge and Prometheus's
`scrape_duration_seconds` over repeated busy cycles. A healthy scrape immediately
after a restart alone does not demonstrate that accumulation is fixed.

### Worker internals (process_batch)

Each worker:

- Closes inherited DB connections (`connections.close_all()`) and opens
  fresh ones, since connections cannot be shared across processes.
- Accumulates parsed instances (issues, checkouts, builds, tests,
  incidents) into an in-memory buffer.
- When any table reaches `INGEST_BATCH_SIZE`, calls `flush_buffers()` with every
  table's buffer in the same transaction. Files are archived only after all their
  records and aggregates commit. A table below the threshold must not be left
  behind in memory after its submission is archived.
- Sorts instances by ID before flushing to prevent deadlocks when
  multiple workers update the same rows concurrently.
- At cycle completion (receiving `None`), flushes any remaining buffered instances,
  closes database connections, and applies the log-excerpt cache size limit.
  Valid submissions containing no records are also archived at cycle completion.

A flush can now include records from all five tables, so a transaction can be
larger than a single table's batch limit. The threshold and file-batch size still
bound when a flush starts; a single large submission can exceed either limit.

### Error handling

- **File parse errors**: The file is moved to the `failed` directory
  and the `stat_fail` counter is incremented. The worker continues
  processing subsequent files. Any other exception raised while preparing a
  file or building its instances is handled the same way, so one bad file
  cannot take a persistent worker down. A file that disappears between the
  spool scan and its batch is skipped.
- **Worker crash**: the parent checks exit codes while idle, feeding the queue,
  and waiting for completion. EOF on a control pipe also reports a worker failure.
  It logs the exit, increments `kcidb_ingester_worker_failures`, and aborts the
  command. Other workers are killed and unarchived files remain for retry.
  A worker killed between its transaction commit and the archive renames leaves
  committed files in the spool; the next run re-ingests them, which the
  `ON CONFLICT` upserts tolerate.
  The counter increment is best effort: the command exits right after it and
  the startup cleanup clears `PROMETHEUS_MULTIPROC_DIR`, so it is rarely
  scraped. Alert on the restart instead, for example
  `resets(kcidb_ingestions_total[1h]) > 0`.
  The process supervisor must restart the command, creating fresh shared queues
  and locks. Replacing a worker in place is unsafe because its abrupt exit can
  leave a shared lock permanently acquired.
- **Signals**: workers ignore SIGINT and SIGTERM. A signal delivered to the whole
  process group (systemd, `docker run --init`) then reaches the parent, which
  finishes the cycle and sends stop messages, instead of aborting worker
  transactions. Only SIGKILL stops a worker early. A container stop grace
  period shorter than a cycle still ends in SIGKILL; the interrupted files stay
  in the spool and are retried on the next start.
- **Worker hang**: Depends on `requests` timeouts (set on all
  production HTTP calls) to eventually unblock the worker.
- **KeyboardInterrupt**: The main process kills all live workers
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
