#!/bin/bash

# Copies data from the DB_DEFAULT to the DASH_DB, through the manage.py update_db command.
#
# The small interval is done in order to avoid running into OOM errors.
# There is no problem in running this script multiple times, as it will only update the database with new data.
#
# Usage in docker:
# docker compose run --build --rm backend sh ./kernelCI_app/backend/scripts/copy_db_data.sh
#
# If OOM errors still occur, lower the INTERVAL_HOURS value

START_DAYS_AGO=7
END_DAYS_AGO=0
INTERVAL_HOURS=8

START_HOURS_AGO=$((START_DAYS_AGO * 24))
END_HOURS_AGO=$((END_DAYS_AGO * 24))

echo "Starting database update from $START_HOURS_AGO hours ago to $END_HOURS_AGO hours ago in $INTERVAL_HOURS hour intervals..."

current_start=$START_HOURS_AGO
while [ $current_start -gt $END_HOURS_AGO ]; do
    current_end=$((current_start - INTERVAL_HOURS))
    
    if [ $current_end -lt $END_HOURS_AGO ]; then
        current_end=$END_HOURS_AGO
    fi
    
    echo "Updating database from $current_start hours ago to $current_end hours ago..."
    poetry run python3 manage.py update_db --start-interval "${current_start} hours" --end-interval "${current_end} hours"
    
    if [ $? -ne 0 ]; then
        echo "Error: Command failed for interval ${current_start} to ${current_end} hours ago"
        exit 1
    fi
    
    current_start=$current_end
done

echo "Database update completed successfully!"
