-- Initialize test databases
-- This script runs when the PostgreSQL container starts for the first time

-- Create the dashboard_test database
CREATE DATABASE dashboard_test;

-- Grant all privileges to the test_user for both databases
GRANT ALL PRIVILEGES ON DATABASE kcidb_test TO test_user;
GRANT ALL PRIVILEGES ON DATABASE dashboard_test TO test_user;

