#!/bin/sh
export PYTHONOPTIMIZE=${PYTHONOPTIMIZE:-2}
export PYTHONUNBUFFERED=${PYTHONUNBUFFERED:-1}

source $(poetry env info -C ./backend --path)/bin/activate
set -e

# usage: file_env VAR [DEFAULT]
#    ie: file_env 'XYZ_DB_PASSWORD' 'example'
# (will allow for "$XYZ_DB_PASSWORD_FILE" to fill in the value of
#  "$XYZ_DB_PASSWORD" from a file, especially for Docker's secrets feature)
function file_env() {
  local var="$1"
  local def="${2:-}"
  local fileVar="${var}_FILE"
  local fileVal=`eval echo \$"${fileVar}"`
  local val=`eval echo \$"${var}"`
  if [ -n "$val" ] && [ -n "$fileVal" ]; then
    echo >&2 "error: both $var and $fileVar are set (but are exclusive)"
    exit 1
  elif [ -f "$fileVal" ]; then
    val=`cat $fileVal`
  elif [ -z "$val" ]; then
    val="$def"
  fi
  export "$var"="$val"
}

file_env DB_PASSWORD

# Initialize Prometheus metrics before Django starts
PROMETHEUS_METRICS_ENABLED=$(echo "$PROMETHEUS_METRICS_ENABLED" | tr '[:upper:]' '[:lower:]')
PROMETHEUS_MULTIPROC_DIR=${PROMETHEUS_MULTIPROC_DIR:-/tmp/prometheus_multiproc_dir}
export PROMETHEUS_MULTIPROC_DIR
mkdir -p "$PROMETHEUS_MULTIPROC_DIR"

if [ "$PROMETHEUS_METRICS_ENABLED" = "true" ]; then
    echo "Initializing Prometheus metrics before Django startup..."
    PROMETHEUS_METRICS_PORT=${PROMETHEUS_METRICS_PORT:-8001}
    export PROMETHEUS_METRICS_PORT

    rm -f $PROMETHEUS_MULTIPROC_DIR/*.db || true

    python3 utils/prometheus_aggregator.py &
fi

chmod +x ./setup-dashboard-db.sh
./setup-dashboard-db.sh

# Add and start cronjobs
poetry run ./manage.py crontab add
# BusyBox crond doesn't support a "start" subcommand.
# Start cronjobs in background and emit logs to container stdout.
crond -b -L /proc/1/fd/1

# Update the sqlite cache db
chmod +x ./migrate-cache-db.sh
./migrate-cache-db.sh

# To update the app db, run MANNUALLY:
# docker compose run --rm backend sh -c "chmod +x ./migrate-app-db.sh && ./migrate-app-db.sh"

exec "$@"
