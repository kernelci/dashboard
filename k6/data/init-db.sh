#!/bin/bash
set -e

# This script will run when the PostgreSQL container starts
# It will restore the database from the dump file if it exists and the database is empty

# Function to check if database has any user tables
check_database_populated() {
    local table_count=$(psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | xargs)
    echo "$table_count"
}

echo "Starting database initialization script..."

if [ -f /docker-entrypoint-initdb.d/dump.sql ]; then
    echo "Found dump.sql file..."
    
    # Check if database is already populated
    table_count=$(check_database_populated)
    
    if [ "$table_count" -gt 0 ]; then
        echo "Database already populated (found $table_count tables). Skipping restore."
    else
        echo "Database appears empty. Restoring from dump..."
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" < /docker-entrypoint-initdb.d/dump.sql
        echo "Database restored successfully!"
    fi
else
    echo "No dump.sql found, database will start empty"
fi
