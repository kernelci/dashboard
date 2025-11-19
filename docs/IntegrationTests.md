# Integration Tests

## Overview

The integration tests present real-world scenarios using a well-organized mock data system that separates data from logic, making it easy to maintain and extend. The system is built around classes that manage different types of test data and fixtures that contain the raw data.

These tests can be executed against both production databases and local databases. However, it is **highly recommended to use the local database** as described in the setup instructions below, as it provides better isolation, faster execution, and safer testing environment.

## Mock Data Structure

### Directory Organization

```
backend/kernelCI_app/tests/factories/
├── mocks/
│   ├── build.py            # Build data management class
│   ├── checkout.py         # Checkout data management class
│   ├── issue.py            # Issue data management class
│   ├── test.py             # Test data management class
│   └── fixtures/
│       ├── build_data.py   # Build data and status rules
│       ├── issue_data.py   # Issue data
│       ├── test_data.py    # Test data and status rules
│       └── tree_data.py    # Checkout and hardware data
├── build_factory.py        # Build factory
├── checkout_factory.py     # Checkout factory
├── incident_factory.py     # Incident factory
├── issue_factory.py        # Issue factory
└── test_factory.py         # Test factory
```

### Data Relationships

The mock data follows a hierarchical relationship:

```
Checkout (1) → (N) Build (1) → (N) Test
     ↓
Hardware Platform

Issue (1) → (N) Incident (N) → (1) Build/Test
```

## Adding New Test Data

### 1. Checkout Data

Checkouts represent kernel trees and are the foundation of the test data hierarchy.

**Files to modify:**
- `mocks/fixtures/tree_data.py`

**Required fields:**
```python
"checkout_id": {
    "origin": "maestro",                    # Required: Origin of the checkout
    "git_url": "https://git.kernel.org/...", # Required: Git repository URL
    "git_branch": "main",                   # Required: Git branch name
    "tree_name": "mainline",                # Required: Tree name
    "start_time": datetime.fromtimestamp(...), # Optional: Specific timestamp
    "hardware_platform": "arm64,board",     # Optional: Hardware platform identifier
}
```

**Example:**
```python
# In mocks/fixtures/tree_data.py
"raspberry_pi_001": {
    "origin": "maestro",
    "git_url": "https://github.com/raspberrypi/linux.git",
    "git_branch": "rpi-6.1.y",
    "tree_name": "raspberry-pi",
    "start_time": datetime.fromtimestamp(1740000000, timezone.utc),
    "hardware_platform": "raspberry-pi,4-model-b",
},
```

### 2. Build Data

Builds are related to checkouts and represent kernel builds for specific architectures.

**Files to modify:**
- `mocks/fixtures/build_data.py`

**Required fields:**
```python
"build_id": {
    "checkout_id": "checkout_id",           # Required: Related checkout ID
    "origin": "maestro",                    # Required: Origin (usually same as checkout)
    "architecture": "arm64",                # Required: Target architecture
    "status": "PASS",                       # Optional: Build status (PASS/FAIL/ERROR/SKIP/MISS/DONE)
    "config_name": "defconfig",             # Optional: Kernel config name
}
```

**Status Rules:**
You can also define checkout-based status rules for builds not explicitly defined:

```python
CHECKOUT_BUILD_STATUS_RULES = {
    "checkout_id": "PASS",  # All builds from this checkout will be PASS
    # ... other rules
}
```

**Example:**
```python
# In mocks/fixtures/build_data.py
"raspberry_pi_build_001": {
    "checkout_id": "raspberry_pi_001",
    "origin": "maestro",
    "architecture": "arm64",
    "status": "PASS",
    "config_name": "bcm2711_defconfig",
},

# Optional: Add status rule
CHECKOUT_BUILD_STATUS_RULES = {
    "raspberry_pi_001": "PASS",  # All builds from raspberry_pi_001 will be PASS
    # ... existing rules
}
```

### 3. Test Data

Tests are related to builds and represent test executions.

**Files to modify:**
- `mocks/fixtures/test_data.py`

**Required fields:**
```python
"test_id": {
    "status": "PASS",                       # Optional: Test status (PASS/FAIL/ERROR/SKIP/MISS/DONE)
    "path": "boot.boot_test",               # Optional: Test path
}
```

**Status Rules:**
Tests can have status determined by:
1. **Test-specific status** (highest priority)
2. **Build-based rules** (medium priority)
3. **Checkout-based rules** (lowest priority)

```python
# Build-based rules
BUILD_TEST_STATUS_RULES = {
    "build_id": "FAIL",  # All tests from this build will be FAIL
    # ... other rules
}

# Checkout-based rules
CHECKOUT_TEST_STATUS_RULES = {
    "checkout_id": "SKIP",  # All tests from this checkout will be SKIP
    # ... other rules
}
```

**Example:**
```python
# In mocks/fixtures/test_data.py
"raspberry_pi_test_001": {
    "status": "PASS",
    "path": "boot.boot_test",
},

# Optional: Add status rules
BUILD_TEST_STATUS_RULES = {
    "raspberry_pi_build_001": "PASS",  # All tests from this build will be PASS
    # ... existing rules
}

CHECKOUT_TEST_STATUS_RULES = {
    "raspberry_pi_001": "PASS",  # All tests from this checkout will be PASS
    # ... existing rules
}
```

### 4. Issue Data

Issues are independent entities that can be related to builds or tests through **incidents**.

**Files to modify:**
- `mocks/fixtures/issue_data.py`

**Required fields:**
```python
"issue_id": {
    "version": 1,                           # Required: Issue version
    "build_ids": ["build_id_1", "build_id_2"], # Optional: Related build IDs
    "test_ids": ["test_id_1", "test_id_2"],    # Optional: Related test IDs
}
```

**Note:** Issues are independent but we create predefined issues that will be related to builds or tests via **incidents** along with the version.

**Example:**
```python
# In mocks/fixtures/issue_data.py
"raspberry_pi_issue_001": {
    "version": 1,
    "build_ids": ["raspberry_pi_build_001"],
    "test_ids": [],
},
```

## Running Integration Tests

### Database Options

The integration tests can be run against different database configurations:

1. **Local Database (Recommended)** - Uses `docker-compose.test.yml` with isolated PostgreSQL
   - Better isolation and safety
   - Faster execution
   - No impact on production data

2. **Production Database** - Uses the main application database
   - Requires careful configuration
   - Tests can be broken depending on the inserted data
   - Slower execution

### Prerequisites

- Docker and Docker Compose
- Poetry (for local development)

### Using Local Database (Recommended)

The integration tests use a dedicated test environment with local PostgreSQL database.

#### 1. Test Environment Configuration

The test environment is configured in `docker-compose.test.yml`:

#### 2. Running Tests Step by Step

**Step 1: Start test database and Redis**
```bash
docker compose -f docker-compose.test.yml up test_db redis -d
```

**Step 2: Execute migrations**
```bash
docker compose -f docker-compose.test.yml run --rm test_backend python manage.py migrate
```

**Step 3: Populate database with test data**
```bash
docker compose -f docker-compose.test.yml run --rm test_backend python manage.py seed_test_data --clear
```

**Step 4: Start test backend**
```bash
docker compose -f docker-compose.test.yml up --build -d
```

**Step 5: Run integration tests**
```bash
cd backend
TEST_BASE_URL=http://localhost:8001 poetry run pytest -m integration --use-local-db --run-all
```

**Step 6: Clean up**
```bash
docker compose -f docker-compose.test.yml down --volumes --remove-orphans
```

>![IMPORTANT] If you run the tests, see a problem and go about fixing it, remember to rebuild the docker containers at Step 4 with `--force-recreate`

### Test Configuration

The test environment uses `backend/kernelCI/test_settings.py` which:

- Configures local PostgreSQL database
- Sets `TEST_BASE_URL=http://localhost:8001/`

### Running Specific Tests

**Run all integration tests:**
```bash
TEST_BASE_URL=http://localhost:8001 poetry run pytest -m integration --use-local-db --run-all
```

**Run only a subset of tests (faster):**
```bash
TEST_BASE_URL=http://localhost:8001 poetry run pytest -m integration --use-local-db
```

**Run specific test file:**
```bash
TEST_BASE_URL=http://localhost:8001 poetry run pytest -m integration --use-local-db backend/kernelCI_app/tests/integrationTests/<your_test>.py
```

**Run specific method:**
```bash
TEST_BASE_URL=http://localhost:8001 poetry run pytest -m integration --use-local-db backend/kernelCI_app/tests/integrationTests/<your_test>.py::<your_function>
```

### Troubleshooting

**Database connection issues:**
- Ensure PostgreSQL is running on **port 5435**
- Check that test_db container is healthy: `docker ps`

**Backend not responding:**
- Check backend logs: `docker logs test_backend_service`
- Verify backend is running on port 8001: `curl http://localhost:8001/`

**Test data issues:**
- Clear and repopulate database: `docker compose -f docker-compose.test.yml run --rm test_backend python manage.py seed_test_data --clear`

**Clean up everything:**
```bash
docker compose -f docker-compose.test.yml down --volumes --remove-orphans
docker system prune -af
```

## Best Practices for local database Integration Tests

1. **Clear data between runs** - Use `--clear` flag when seeding test data
2. **Use meaningful IDs** - Make test data IDs descriptive and consistent
3. **Follow the hierarchy** - Always create checkouts before builds, builds before tests
4. **Test locally first** - Run tests locally before pushing to CI

## CI/CD Integration

The integration tests are automatically run in CI/CD using the same Docker Compose setup. The CI environment:

- Uses `docker-compose.test.yml` for test services
- Runs migrations and seeds test data automatically
- Executes tests with coverage reporting
- Cleans up resources after completion

See `.github/workflows/ci.yaml` for the complete CI configuration.
