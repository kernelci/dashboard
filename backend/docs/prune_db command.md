# prune_db Command Documentation

The `prune_db` command deletes old rows from `checkouts`, `builds`, and `tests` in the dashboard database. It is intended for routine retention: run with `--dry-run` first, review the counts, then execute without `--dry-run`.

Models use `DO_NOTHING` foreign keys, so the command applies manual cascade rules instead of relying on the database:

- An old checkout also removes its builds and tests, even when those children are newer than the cutoff.
- An old build also removes its tests, even when they are newer than the cutoff.

## Parameters

### Required Parameters

- `--older-than`: Delete rows older than this age. Format: `'x days'`, `'x hours'`, or `'x minutes'` (for example, `'30 days'`).

### Optional Parameters

- `--tables`: Limit pruning to specific tables (comma-separated). Valid options: `checkouts`, `builds`, `tests`. Default: all three.
  - Cascade only drags a child when the child's parent table is also selected. For example, `--tables tests` removes only tests past the cutoff; recent tests under an old build/checkout are kept because those parents are not being pruned. With `--tables builds,tests`, an old build still drags its recent tests, but an old checkout does not drag its recent builds (checkouts are not selected).
  - Tables not listed are not deleted. For example, `--tables builds` removes old builds but leaves their tests in place. Selecting a parent without its children (e.g. only `checkouts`) can therefore leave orphaned rows.
- `--origins`: Limit age-based pruning to specific origins (comma-separated). If omitted, any origin is considered.
  - Cascade ignores origin: once a parent row is doomed, its children are removed even if they belong to a different origin.
- `--batch-size`: Number of rows deleted per batch (default: `10000`). Must be at least `1`.
- `--skip-issue-protection`: Prune builds and tests linked to issues. By default, rows with an associated incident are kept.
- `--dry-run`: Print counts without deleting anything.
- `--yes`: Skip the confirmation prompt and delete immediately.

## Examples

### Preview what would be deleted

```bash
python manage.py prune_db --older-than "30 days" --dry-run
```

### Delete rows older than 90 days

```bash
python manage.py prune_db --older-than "90 days" --yes
```

### Prune only one origin

```bash
python manage.py prune_db --older-than "30 days" --origins maestro,0dayci --dry-run
```

### Prune only tests

```bash
python manage.py prune_db --older-than "30 days" --tables tests --yes
```

### Prune rows linked to issues (override default protection)

```bash
python manage.py prune_db --older-than "30 days" --skip-issue-protection --yes
```

## What Is Not Deleted

The command only touches `checkouts`, `builds`, and `tests`. Related tables are left as-is, including:

- `incidents` rows themselves (only used to decide which builds/tests/checkouts to keep)
- `hardware_status`, `latest_checkout`, `tree_tests_rollup` (reference checkouts)
- `pending_build`, `pending_test` (reference builds)

If those tables must stay consistent, plan separate cleanup or accept stale references until another process removes them.

## Recommended Workflow

1. Run with `--dry-run` and review per-table counts.
2. Add `--origins` when retention should apply to specific origins only.
3. Use `--tables` only when you intentionally want a partial prune.
4. Run without `--dry-run`; confirm at the prompt unless `--yes` is set.

## Notes

- Deletion is batched and child-first (`tests`, then `builds`, then `checkouts`) to avoid orphans within the pruned set.
- Each batch commits separately to keep locks short.
- `--origins` scopes the age filter only. Cascade deletions do not re-check the child's origin.
- By default, builds and tests referenced by `incidents` are not pruned, and their parent checkouts are kept too. Use `--skip-issue-protection` to delete them anyway (incident rows are not removed by this command).
