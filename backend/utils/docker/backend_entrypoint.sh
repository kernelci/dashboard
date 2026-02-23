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

file_env DB_DEFAULT_PASSWORD

# Initialize Prometheus metrics before Django starts
PROMETHEUS_METRICS_ENABLED=$(echo "$PROMETHEUS_METRICS_ENABLED" | tr '[:upper:]' '[:lower:]')
if [ "$PROMETHEUS_METRICS_ENABLED" = "true" ]; then
    echo "Initializing Prometheus metrics before Django startup..."
    PROMETHEUS_METRICS_PORT=${PROMETHEUS_METRICS_PORT:-8001}
    PROMETHEUS_MULTIPROC_DIR=${PROMETHEUS_MULTIPROC_DIR:-/tmp/prometheus_multiproc_dir}
    export PROMETHEUS_MULTIPROC_DIR
    export PROMETHEUS_METRICS_PORT
    
    rm -f $PROMETHEUS_MULTIPROC_DIR/*.db || true
    
    python3 utils/prometheus_aggregator.py &
fi

export DB_DEFAULT="{
    \"ENGINE\": \"${DB_DEFAULT_ENGINE:=django.db.backends.postgresql}\",
    \"NAME\": \"${DB_DEFAULT_NAME:=dashboard}\",
    \"USER\": \"${DB_DEFAULT_USER:=admin}\",
    \"PASSWORD\": \"$DB_DEFAULT_PASSWORD\",
    \"HOST\": \"${DB_DEFAULT_HOST:=dashboard_db}\",
    \"PORT\": \"${DB_DEFAULT_PORT:=5432}\",
    \"CONN_MAX_AGE\": ${DB_DEFAULT_CONN_MAX_AGE:=null},
    \"OPTIONS\": {
      \"connect_timeout\": ${DB_DEFAULT_TIMEOUT:=16}
    }
}"

chmod +x ./utils/docker/setup-dashboard-db.sh
./utils/docker/setup-dashboard-db.sh

# Add and start cronjobs
poetry run ./manage.py crontab add
crond start

# Update the sqlite cache db
chmod +x ./migrate-cache-db.sh
./migrate-cache-db.sh

# To update the app db, run MANNUALLY:
# docker compose run --rm backend sh -c "chmod +x ./migrate-app-db.sh && ./migrate-app-db.sh"

exec "$@"
