poetry run python3 manage.py makemigrations kernelCI_app

if [ "$(echo "${USE_DASHBOARD_DB}" | tr '[:upper:]' '[:lower:]')" = "true" ]; then
    DB_NAME="default"
else
    DB_NAME="dashboard_db"
fi

poetry run python3 manage.py migrate --database="$DB_NAME" --verbosity 3
