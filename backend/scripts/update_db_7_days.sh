# Runs the update_db command for the last 7 days in intervals of 8 hours. This is done in order to avoid running into OOM errors.
# There is no problem in running this script multiple times, as it will only update the database with new data.
#
# Usage:
# docker compose run --build --rm backend sh ./kernelCI_app/management/commands/update_db_7_days.sh
#
# If OOM errors still occur, lower the gap between start/end intervals
poetry run python3 manage.py update_db --start-interval '168 hours' --end-interval '160 hours'
poetry run python3 manage.py update_db --start-interval '160 hours' --end-interval '152 hours'
poetry run python3 manage.py update_db --start-interval '152 hours' --end-interval '144 hours'
poetry run python3 manage.py update_db --start-interval '144 hours' --end-interval '136 hours'
poetry run python3 manage.py update_db --start-interval '136 hours' --end-interval '128 hours'
poetry run python3 manage.py update_db --start-interval '128 hours' --end-interval '120 hours'
poetry run python3 manage.py update_db --start-interval '120 hours' --end-interval '112 hours'
poetry run python3 manage.py update_db --start-interval '112 hours' --end-interval '104 hours'
poetry run python3 manage.py update_db --start-interval '104 hours' --end-interval '96 hours'
poetry run python3 manage.py update_db --start-interval '96 hours' --end-interval '88 hours'
poetry run python3 manage.py update_db --start-interval '88 hours' --end-interval '80 hours'
poetry run python3 manage.py update_db --start-interval '80 hours' --end-interval '72 hours'
poetry run python3 manage.py update_db --start-interval '72 hours' --end-interval '64 hours'
poetry run python3 manage.py update_db --start-interval '64 hours' --end-interval '56 hours'
poetry run python3 manage.py update_db --start-interval '56 hours' --end-interval '48 hours'
poetry run python3 manage.py update_db --start-interval '48 hours' --end-interval '40 hours'
poetry run python3 manage.py update_db --start-interval '40 hours' --end-interval '32 hours'
poetry run python3 manage.py update_db --start-interval '32 hours' --end-interval '24 hours'
poetry run python3 manage.py update_db --start-interval '24 hours' --end-interval '16 hours'
poetry run python3 manage.py update_db --start-interval '16 hours' --end-interval '8 hours'
poetry run python3 manage.py update_db --start-interval '8 hours' --end-interval '0 hours'
