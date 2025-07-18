poetry run python3 manage.py makemigrations kernelCI_app
poetry run python3 manage.py migrate --database=dashboard_db --verbosity 3
