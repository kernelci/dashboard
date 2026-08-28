#!/bin/sh
set -eu

export DB_SESSION_OPTIONS="${DB_SESSION_OPTIONS:--c lock_timeout=30000 -c statement_timeout=3600000}"

poetry run python3 manage.py makemigrations kernelCI_app
poetry run python3 manage.py migrate --verbosity 3
