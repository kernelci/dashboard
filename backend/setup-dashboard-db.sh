#!/bin/sh
# Initializes dashboard database roles and databases via direct psql.
set -eu

# Resolve env vars: prefer explicit names, fall back to backend naming (DB_*)
export DB_HOST="${DB_HOST:-dashboard_db}"
export DB_PORT="${DB_PORT:-5432}"
export DB_PASSWORD="${DB_PASSWORD:?DB_PASSWORD is required}"
export DB_USER="${DB_USER:-admin}"
export DB_NAME="${DB_NAME:-dashboard}"
export APP_DB_USER="${APP_DB_USER:-${DB_USER:?Either APP_DB_USER or DB_USER is required}}"
export APP_DB="${APP_DB:-${DB_NAME:?Either APP_DB or DB_NAME is required}}"

echo "Initializing dashboard database on ${DB_HOST}:${DB_PORT}..."
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres <<SQL
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${DB_USER}') THEN
        CREATE ROLE "${DB_USER}" LOGIN PASSWORD '${DB_PASSWORD}';
    ELSE
        ALTER ROLE "${DB_USER}" WITH LOGIN PASSWORD '${DB_PASSWORD}';
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${APP_DB_USER}') THEN
        CREATE ROLE "${APP_DB_USER}" LOGIN PASSWORD '${DB_PASSWORD}';
    ELSE
        ALTER ROLE "${APP_DB_USER}" WITH LOGIN PASSWORD '${DB_PASSWORD}';
    END IF;
END
\$\$;

SELECT format('CREATE DATABASE %I OWNER %I', '${DB_NAME}', '${DB_USER}')
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')
\\gexec

SELECT format('CREATE DATABASE %I OWNER %I', '${APP_DB}', '${APP_DB_USER}')
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${APP_DB}')
\\gexec

GRANT ALL PRIVILEGES ON DATABASE "${DB_NAME}" TO "${DB_USER}";
GRANT ALL PRIVILEGES ON DATABASE "${APP_DB}" TO "${APP_DB_USER}";
SQL
echo "Dashboard database initialization complete."
