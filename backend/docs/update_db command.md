# update_db Command Documentation

The `update_db` command snapshots dashboard tables to a `.tar.gz` and restores them. Most tables are limited to `--start-interval` / `--end-interval`. `commits` and `commit_parents` are copied in full for now (no time filter), so git ancestry is not cut when a parent has no checkout in the window. A later change may slice those tables.

The migration preserves foreign key constraints. For example, if a test A references a build B in kcidb, but the build B doesn't exist in dashboard_db, then the test A will not be inserted in dashboard_db.

## Parameters

### Required Parameters

- `--start-interval`: Start interval for filtering data (format: 'x days' or 'x hours'). The format follows the SQL filtering format. Does not apply to `commits` or `commit_parents`.
- `--end-interval`: End interval for filtering data (format: 'x days' or 'x hours'). The format follows the SQL filtering format. Does not apply to `commits` or `commit_parents`.

### Optional Parameters

- `--table`: Limit data copy to a specific table
  - Valid options: `issues`, `checkouts`, `commits`, `commit_parents`, `builds`, `tests`, `incidents`, `latest_checkout`, `hardware_status`, `tree_listing`, `tree_tests_rollup`
  - If not provided, data from all tables will be copied
- `--related-data-only`: Limits the selected data to data where the foreign key constraint is not broken.
  - Default: False.
- `--origins`: Limits the selected data to specific origins formatted as a comma-separated string.
  - If not provided, data from all origins will be copied

## Examples

### Migrate all tables for the last 7 days
```bash
python manage.py update_db --start-interval "7 days" --end-interval "0 days"
```

### Migrate only builds table for the last 24 hours
```bash
python manage.py update_db --start-interval "1 days" --end-interval "0 days" --table builds
```

## Migration Process

1. **Data Selection**: Selects records from the default database within the specified time range, except `commits` and `commit_parents` (full table)
2. **Relationship Validation**: Ensures foreign key constraints are maintained
3. **Data Insertion**: Inserts valid data into the dashboard db
4. **Conflict Resolution**: Uses `ignore_conflicts=True` to handle duplicate records

## Notes

- Migration preserves JSON fields by parsing them appropriately
- The skipped rows count are related to rows which didn't have relationships in dashboard_db. The processed rows count are related to the remaining rows that were selected but not skipped (even if they were inserted or had a conflict, which is how django returns the `bulk_create` result)
- `commits` and `commit_parents` are not filtered by time or origin. The full git graph is dumped so ancestors without a checkout in the window are kept. Time slicing may be added later.
- Surrogate ids are kept as in the source. Restore runs `setval` to `MAX(id)` so the next insert does not collide.

## Performance Considerations

- Use appropriate time intervals to avoid processing too much data at once
- The command uses different batch sizes optimized for each table type
