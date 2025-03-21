poetry run python3 manage.py makemigrations kernelCI_cache
poetry run python3 manage.py migrate --database=cache
