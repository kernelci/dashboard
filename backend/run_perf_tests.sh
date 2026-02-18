#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$SCRIPT_DIR/tests_submissions/archive"
mkdir -p "$SCRIPT_DIR/tests_submissions/failed"

cd "$SCRIPT_DIR"

export DJANGO_SETTINGS_MODULE=kernelCI.perf_test_settings
export TEST_DB_HOST=localhost
export TEST_DB_PORT=5435

poetry run pytest -m performance -n 0 --reuse-db --benchmark-time-unit=s --benchmark-autosave "$@"
