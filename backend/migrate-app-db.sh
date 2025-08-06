poetry run python3 manage.py makemigrations kernelCI_app

# If the dashboard_db is set as default, change the database name to default or omit it
poetry run python3 manage.py migrate --database=dashboard_db --verbosity 3
