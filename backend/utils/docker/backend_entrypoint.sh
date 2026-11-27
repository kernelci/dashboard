#!/bin/sh
export PYTHONOPTIMIZE=${PYTHONOPTIMIZE:-2}
export PYTHONUNBUFFERED=${PYTHONUNBUFFERED:-1}

source $(poetry env info --path)/bin/activate
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


# Tree name data and an optional notifications.sqlite3 live here.
export BACKEND_VOLUME_DIR=${BACKEND_VOLUME_DIR:-/volume_data}
mkdir -p "$BACKEND_VOLUME_DIR"

# Update the MAIN db (includes notification tables)
chmod +x ./migrate-app-db.sh
./migrate-app-db.sh

# Copy notification history off sqlite when an existing deploy still has the file.
poetry run ./manage.py import_notification_sqlite

# Add and start cronjobs in background and emit logs to container stdout.
poetry run ./manage.py crontab add
crond -b -L /proc/1/fd/1


exec "$@"
