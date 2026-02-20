#!/bin/sh
# Initializes dashboard database roles and databases via direct psql.
# Works both from a host (cicd/) and inside the backend container entrypoint.
# Canonical copy lives in cicd/setup-dashboard-db.sh — keep both in sync.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Resolve env vars: prefer explicit names, fall back to backend naming (DASH_DB_*, DB_DEFAULT_*)
export DB_HOST="${DB_HOST:-${DASH_DB_HOST:-127.0.0.1}}"
export DB_PORT="${DB_PORT:-${DASH_DB_PORT:-5432}}"
export DB_PASSWORD="${DB_PASSWORD:-${DASH_DB_PASSWORD:?Either DB_PASSWORD or DASH_DB_PASSWORD is required}}"
export DASHBOARD_DB_USER="${DASHBOARD_DB_USER:-${DASH_DB_USER:?Either DASHBOARD_DB_USER or DASH_DB_USER is required}}"
export APP_DB_USER="${APP_DB_USER:-${DB_DEFAULT_USER:?Either APP_DB_USER or DB_DEFAULT_USER is required}}"
export DASHBOARD_DB="${DASHBOARD_DB:-${DASH_DB_NAME:?Either DASHBOARD_DB or DASH_DB_NAME is required}}"
export APP_DB="${APP_DB:-${DB_DEFAULT_NAME:?Either APP_DB or DB_DEFAULT_NAME is required}}"

TEMPLATE="${SCRIPT_DIR}/init-dashboard-db.sql.tpl"
TMP_SQL="$(mktemp)"
trap 'rm -f "$TMP_SQL"' EXIT

python3 - "$TMP_SQL" "$TEMPLATE" <<'PY'
import os
import sys
from pathlib import Path

out_file, template_file = sys.argv[1:3]
template = Path(template_file).read_text()

replacements = {
    "{{DASHBOARD_DB_USER}}": os.environ["DASHBOARD_DB_USER"],
    "{{APP_DB_USER}}": os.environ["APP_DB_USER"],
    "{{DASHBOARD_DB}}": os.environ["DASHBOARD_DB"],
    "{{APP_DB}}": os.environ["APP_DB"],
    "{{DB_PASSWORD}}": os.environ["DB_PASSWORD"],
}

for token, value in replacements.items():
    template = template.replace(token, value)

Path(out_file).write_text(template)
PY

if [ ! -f "$TMP_SQL" ]; then
    echo >&2 "Generated SQL file missing: $TMP_SQL"
    exit 1
fi

echo "Initializing dashboard database on ${DB_HOST}:${DB_PORT}..."
PGPASSWORD="$DB_PASSWORD" \
  psql -h "$DB_HOST" -p "$DB_PORT" -U "$DASHBOARD_DB_USER" -d postgres < "$TMP_SQL"
echo "Dashboard database initialization complete."
