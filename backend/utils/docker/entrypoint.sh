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

export DB_DEFAULT="{
    \"ENGINE\": \"${DB_DEFAULT_ENGINE:=django.db.backends.postgresql}\",
    \"NAME\": \"${DB_DEFAULT_NAME:=kcidb}\",
    \"USER\": \"${DB_DEFAULT_USER:=kernelci}\",
    \"PASSWORD\": \"$DB_DEFAULT_PASSWORD\",
    \"HOST\": \"${DB_DEFAULT_HOST:=cloudsql-proxy}\",
    \"PORT\": \"${DB_DEFAULT_PORT:=5432}\",
    \"CONN_MAX_AGE\": ${DB_DEFAULT_CONN_MAX_AGE:=null},
    \"OPTIONS\": {
      \"connect_timeout\": ${DB_DEFAULT_TIMEOUT:=16}
    }
}"

if [ "$SETUP_DJANGO" = 1 ]; then
    ./manage.py migrate --noinput
    exit 0
fi

# Bring back new local files from backend to the docker volume
echo "Copying backend data backup to volume"
rsync -av --ignore-existing /tmp/backend_data_backup/. /backend/data/
rm -rf /tmp/backend_data_backup

# Add and start cronjobs
poetry run ./manage.py crontab add
crond start

# Update the sqlite cache db
chmod +x ./migrate-cache-db.sh
./migrate-cache-db.sh


exec "$@"
