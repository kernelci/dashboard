# monitor_submissions Command Documentation

The `monitor_submissions` command is a file monitoring and ingestion service that continuously processes KernelCI submission data from a spool directory. It monitors for new JSON files containing any database object data (tests, builds, ...), processes them in parallel, and ingests them into the database.

## Overview

This command implements a robust ingestion pipeline that:
- Monitors a spool directory for new JSON files
- Processes files in parallel using configurable worker threads
- Validates and transforms submission data
- Handles log excerpts by uploading large ones to external storage
- Inserts data into the database using Django models and ORM
- Archives successfully processed files to prevent reprocessing
- Maintains data integrity with proper error handling and file management


## Parameters

### Required Parameters

- `--spool-dir`: Path to the spool directory containing JSON files and required subfolders (`failed/` and `archive/`)

### Optional Parameters

- `--max-workers`: Maximum number of worker threads for parallel processing (default: 5)
- `--interval`: Check interval in seconds between directory scans (default: 5)
- `--trees-file`: Path to YAML file mapping tree names to their URLs (overrides default path "/app/trees.yaml")

### Environment Variables

The command uses the following environment variables:

- `STORAGE_TOKEN`: Bearer token for uploading log excerpts to external storage
- `STORAGE_BASE_URL`: Base URL for storage service (default: "https://files-staging.kernelci.org")

If `STORAGE_TOKEN` is not set, log_excerpts will not be uploaded and the original log_excerpt will be inserted in the database.

### On Docker

It is possible to run the ingester within docker, as visible in the [docker-compose file](/docker-compose.yml). If you want to test it there, it is suggested to change the volume mount from `../spool` to just `./backend/spool`, which will allow you to interact with it from inside the project files.

If you have permission errors with the directory, try fixing it with `sudo chown -R $USER:$USER ./backend/spool` as this will change the ownership from docker to your user.

## Directory Structure

The spool directory must have the following structure:
```
spool-dir/
├── *.json          # Input files to be processed
├── failed/         # Files that failed processing
└── archive/        # Successfully processed files
```

The command will automatically create missing subdirectories if they don't exist.


## Processing Pipeline

### 1. File Discovery
- Scans the spool directory for `.json` files every `interval` seconds
- Ignores empty files (deletes them automatically)

### 2. Parallel Processing
- Uses ThreadPoolExecutor with configurable `max-workers`
- Each file is processed in a separate thread for I/O operations
- Database operations are serialized through a single worker thread

### 3. Data Transformation
- **Tree Name Standardization**: Maps git repository URLs to standardized tree names using trees.yaml
- **Log Excerpt Processing**: Large log excerpts (>256 bytes) are uploaded to external storage and replaced with URLs
- **Schema Validation**: Validates data against KernelCI schema using library `kcidb-io`
- **Schema Upgrade**: Upgrades data to the latest schema version if not already up to date

### 4. File Management
- **Success**: Files are moved to `archive/` subdirectory
- **Failure**: Files are moved to `failed/` subdirectory
- **Empty**: Files are deleted immediately

### 5. Cache Maintenance
- Maintains an in-memory cache of uploaded log excerpts to avoid duplicate uploads
- Automatically clears cache when it exceeds 100,000 entries (arbitrary limit set by `CACHE_LOGS_SIZE_LIMIT` variable)


## Examples

### Basic Usage
```bash
python manage.py monitor_submissions --spool-dir /path/to/spool
```

### High-Throughput Configuration
```bash
python manage.py monitor_submissions \
    --spool-dir /path/to/spool \
    --max-workers 10 \
    --interval 2
```

### Custom Trees Configuration
```bash
python manage.py monitor_submissions \
    --spool-dir /path/to/spool \
    --trees-file /custom/path/trees.yaml
```

## Error Handling

### Processing Errors
- **JSON Parse Errors**: Invalid JSON files are moved to `failed/`
- **Schema Validation Errors**: Files that don't match KernelCI schema are moved to `failed/`
- **Database Errors**: Ignores data and logs error to console, without stopping the execution
- **Logexcerpt Storage Upload Errors**: Falls back to storing original log excerpt in database if upload fails.

### Recovery
- Failed files remain in `failed/` directory for manual inspection
- The command can be restarted safely - it will resume processing new files
- Archived files are preserved and won't be reprocessed


## Integration Notes

- Part of the KernelCI dashboard ingestion pipeline
- Designed to work with KernelCI data submission format (schema v5.3)
- Integrates with external storage service for log excerpt management
- Uses Django ORM for database operations through `insert_submission_data`
- Command ported from the [kcidb-ng repository](https://github.com/kernelci/kcidb-ng) on [PR 1372](https://github.com/kernelci/dashboard/pull/1372)
