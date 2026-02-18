# Performance Testing

This project includes two types of performance testing:

1. **K6 Testing** - For API endpoint load testing
2. **Pytest-Benchmark** - For backend component performance benchmarking

---

## K6 Testing Framework

K6 is used for performance and load testing of API endpoints.

### Quick Start

Run tests using Docker Compose:

```bash
docker-compose -f docker-compose.k6.yml up
```

The Docker setup handles all K6 dependencies automatically.

### Project Structure

- **Test files**: Place your K6 test scripts in `./k6/tests/`
- **Results**: Test outputs are saved to `./k6/results/`
- **Dataset**: Test data should be placed in `./k6/data`. See `./k6/data/README.md` for initialization instructions.

### Configuration

By default, the docker compose command will run all .js files in `./k6/tests/`, but you can send more arguments to the docker command (in the docker-compose file or when using docker run) to specify the file that you want to run.

## pytest-benchmark Performance Tests

pytest-benchmark is used for performance benchmarking of backend components such as the ingester.

### Prerequisites

1. **Test Database**: You need a running test database. Start it with:

   ```bash
   docker compose -f docker-compose.test.yml up test_db -d
   ```

### Running Performance Tests

#### Local Execution

The easiest way to run performance tests locally is using the provided script:

```bash
cd backend
./run_perf_tests.sh
```

This script:

- Sets the correct database connection parameters
- Runs pytest with the `performance` marker
- Disables parallel execution (required for accurate benchmarks with pytest-benchmark)

#### Manual Execution

You can also run performance tests manually with more control:

```bash
cd backend
export DJANGO_SETTINGS_MODULE=kernelCI.perf_test_settings
export TEST_DB_HOST=localhost
export TEST_DB_PORT=5435
poetry run pytest -m performance --use-local-db -n 0
```

#### Running Specific Performance Tests

To run a specific performance test file:

```bash
cd backend
./run_perf_tests.sh kernelCI_app/tests/performanceTests/test_ingest_perf.py
```

### Understanding the Output

Performance tests generate detailed statistics including:

- **Mean execution time**: Average time taken across all rounds
- **Standard deviation**: Variability in execution times
- **Min/Max times**: Fastest and slowest execution times

Example output:

```
test_ingest_perf
  Mean: 8.23s
  Std Dev: 0.45s
  Min: 7.89s
  Max: 9.01s
```

### Benchmark Results Storage

pytest-benchmark automatically saves detailed benchmark results to a `.benchmarks` folder in JSON format. This folder contains comprehensive performance data including:

- Historical benchmark runs
- Detailed timing statistics for each test
- Comparison data between runs
- Additional metadata about the test execution environment

### Important Notes

- **Performance thresholds**: Tests assert mean execution time < 10s. This may vary on different hardware or CI environments.
- **Database setup**: Uses dedicated `perf_test_settings.py` which enables migrations for proper schema setup.
- **Parallel execution**: Must run with `-n 0` (no parallel execution) for accurate benchmarking and avoid conflicts with pytest-benchmark.
- **File cleanup**: Tests automatically backup and restore submission files between rounds.
