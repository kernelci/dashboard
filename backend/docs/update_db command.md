# update_db Command Documentation

The `update_db` command migrates data from the default database (kcidb) to the dashboard_db database within a specified time interval. All tables are updated by default, but you can select a specific one as well.

The migration preserves foreign key constraints. For example, if a test A references a build B in kcidb, but the build B doesn't exist in dashboard_db, then the test A will not be inserted in dashboard_db.

## Parameters

### Required Parameters

- `--start-interval`: Start interval for filtering data (format: 'x days' or 'x hours'). The format follows the SQL filtering format.
- `--end-interval`: End interval for filtering data (format: 'x days' or 'x hours'). The format follows the SQL filtering format.

### Optional Parameters

- `--table`: Limit migration to a specific table (optional)
  - Valid options: `issues`, `checkouts`, `builds`, `tests`, `incidents`
  - If not provided, all tables will be migrated

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

1. **Data Selection**: Selects records from the default database within the specified time range
2. **Relationship Validation**: Ensures foreign key constraints are maintained
3. **Data Insertion**: Inserts valid data into the dashboard db
4. **Conflict Resolution**: Uses `ignore_conflicts=True` to handle duplicate records

## Notes

- Migration preserves JSON fields by parsing them appropriately
- The skipped rows count are related to rows which didn't have relationships in dashboard_db. The processed rows count are related to the remaining rows that were selected but not skipped (even if they were inserted or had a conflict, which is how django returns the `bulk_create` result)

## Performance Considerations

- Use appropriate time intervals to avoid processing too much data at once
- The command uses different batch sizes optimized for each table type
