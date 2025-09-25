#!/bin/sh

echo "=================================="
echo "Starting All K6 Performance Tests"
echo "=================================="

# Check if database is accessible
echo "Testing database connection..."
if nc -z k6-db 5432; then
    echo "Database is accessible"
else
    echo "Database not accessible"
    exit 1
fi

echo "Running K6 tests..."

# Reusable function for a single test file
run_single_test() {
    test_file=$1
    echo "Running test: $test_file"
    
    k6 run \
        --summary-export="/results/${test_arg}_summary_${TIMESTAMP}.json" \
        --summary-trend-stats="avg,min,med,max,p(95),p(99)" \
        "$test_file"
        
    echo "Completed test: $test_file"
    echo "Results exported to /results/"
    echo "-------------------"
}


# Get current timestamp for unique file names
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Check if specific test files were provided as arguments
if [ $# -gt 0 ]; then
    echo "Running specific test files: $@"
    
    for test_arg in "$@"; do
        test_file="./tests/${test_arg}.js"
        
        if [ -f "$test_file" ]; then
            run_single_test "$test_file"
        else
            echo "Warning: Test file '$test_file' not found, skipping..."
        fi
    done
else
    echo "No specific tests provided, running all tests in ./tests/ directory"
    
    for test_file in ./tests/*.js; do
        if [ -f "$test_file" ]; then
            test_name=$(basename "$test_file" .js)
            run_single_test "$test_name"
        fi
    done
fi

echo "All tests completed!"
echo "Results available in /results/ directory"
