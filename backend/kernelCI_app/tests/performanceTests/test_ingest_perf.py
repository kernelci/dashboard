import glob
import json
import os
import shutil
import zipfile
from typing import Any
from unittest.mock import patch

import kcidb_io
import pytest

from kernelCI_app.management.commands.helpers.kcidbng_ingester import (
    MAP_TABLENAMES_TO_COUNTER,
    SubmissionFileMetadata,
    flush_buffers,
    ingest_submissions_parallel,
    prepare_file_data,
)
from kernelCI_app.management.commands.helpers.process_submissions import (
    build_instances_from_submission,
)

trees_names = {
    "mainline": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
}

SUBMISSIONS_DIR = "tests_submissions"
SUBMISSIONS_BACKUP_DIR = "tests_submissions_backup"
SUBMISSIONS_ZIP = os.path.join(SUBMISSIONS_DIR, "submissions.zip")


WORKER_COUNTS = [1, 3, 5]
BATCH_SIZES = [1000, 5000, 10000]
FILE_SUBSETS = [100, 300, 500]


def _load_submission_files(dir_path: str) -> list[os.DirEntry[str]]:
    with os.scandir(dir_path) as it:
        return [
            entry for entry in it if entry.is_file() and entry.name.endswith(".json")
        ]


def _restore_submission_files(*args, **kwargs) -> None:
    """Restore submission files from backup after each benchmark iteration."""

    if os.path.exists(SUBMISSIONS_BACKUP_DIR):
        if os.path.exists(SUBMISSIONS_DIR):
            shutil.rmtree(SUBMISSIONS_DIR)
        shutil.copytree(SUBMISSIONS_BACKUP_DIR, SUBMISSIONS_DIR)


@pytest.fixture(scope="session", autouse=True)
def setup_dashboard_db(django_db_blocker):
    """Create tables in database for performance tests."""
    from django.core.management import call_command

    with django_db_blocker.unblock():
        call_command(
            "migrate",
            "kernelCI_app",
            database="default",
        )


def _unzip_submissions():
    """Unzip submissions.zip if it exists."""
    if os.path.exists(SUBMISSIONS_ZIP):
        with zipfile.ZipFile(SUBMISSIONS_ZIP, "r") as zip_ref:
            zip_ref.extractall(SUBMISSIONS_DIR)


def _delete_json_files():
    """Delete all JSON files in the submissions directory."""
    json_files = glob.glob(os.path.join(SUBMISSIONS_DIR, "*.json"))
    for json_file in json_files:
        try:
            os.remove(json_file)
        except OSError:
            pass


@pytest.fixture
def cleanup_submission_files():
    """
    Fixture to backup and restore submission files after test execution.
    Files are moved during ingestion, this ensures they return to original location.
    """
    _unzip_submissions()

    if os.path.exists(SUBMISSIONS_DIR):
        shutil.copytree(SUBMISSIONS_DIR, SUBMISSIONS_BACKUP_DIR, dirs_exist_ok=True)

    yield

    if os.path.exists(SUBMISSIONS_BACKUP_DIR):
        if os.path.exists(SUBMISSIONS_DIR):
            shutil.rmtree(SUBMISSIONS_DIR)
        shutil.copytree(SUBMISSIONS_BACKUP_DIR, SUBMISSIONS_DIR)
        shutil.rmtree(SUBMISSIONS_BACKUP_DIR)

    _delete_json_files()


def _get_file_subset(
    files: list[os.DirEntry[str]], subset: int
) -> list[os.DirEntry[str]]:
    """Get a subset of files based on the subset type."""
    return files[:subset] if len(files) >= subset else files


@pytest.mark.django_db(transaction=True)
@pytest.mark.benchmark(group="ingest-parallel-workers")
@pytest.mark.parametrize("max_workers", WORKER_COUNTS)
def test_ingest_perf_workers(
    benchmark, cleanup_submission_files, max_workers
):  # noqa: ARG001
    """Benchmark ingestion performance with different worker counts."""
    files = _load_submission_files(SUBMISSIONS_DIR)

    assert len(files) > 0, "No submissions found"

    benchmark.pedantic(
        ingest_submissions_parallel,
        args=(
            files,
            trees_names,
            os.path.join(SUBMISSIONS_DIR, "archive"),
            os.path.join(SUBMISSIONS_DIR, "failed"),
            max_workers,
        ),
        rounds=5,
        iterations=1,
        teardown=_restore_submission_files,
    )

    files_per_second = len(files) / benchmark.stats.stats.mean

    benchmark.extra_info["files_processed"] = len(files)
    benchmark.extra_info["max_workers"] = max_workers
    benchmark.extra_info["files_per_second"] = f"{files_per_second:.2f}"


@pytest.mark.django_db(transaction=True)
@pytest.mark.benchmark(group="ingest-parallel-file-count")
@pytest.mark.parametrize("file_subset", FILE_SUBSETS)
def test_ingest_perf_file_count(
    benchmark, cleanup_submission_files, file_subset
):  # noqa: ARG001
    """Benchmark ingestion performance with different file counts."""
    all_files = _load_submission_files(SUBMISSIONS_DIR)
    files = _get_file_subset(all_files, file_subset)

    assert len(files) > 0, "No submissions found"

    benchmark.pedantic(
        ingest_submissions_parallel,
        args=(
            files,
            trees_names,
            os.path.join(SUBMISSIONS_DIR, "archive"),
            os.path.join(SUBMISSIONS_DIR, "failed"),
            3,
        ),
        rounds=5,
        iterations=1,
        teardown=_restore_submission_files,
    )

    files_per_second = len(files) / benchmark.stats.stats.mean

    benchmark.extra_info["files_processed"] = len(files)
    benchmark.extra_info["file_subset"] = file_subset
    benchmark.extra_info["files_per_second"] = f"{files_per_second:.2f}"


@pytest.mark.benchmark(group="validation-and-upgrade")
@pytest.mark.parametrize("file_subset", FILE_SUBSETS)
def test_validation_and_upgrade(benchmark, cleanup_submission_files, file_subset):
    all_files = _load_submission_files(SUBMISSIONS_DIR)
    files = _get_file_subset(all_files, file_subset)

    def validate_files(files):
        for file in files:
            with open(file, "r") as f:
                data = json.loads(f.read())
            kcidb_io.schema.V5_3.validate(data)
            kcidb_io.schema.V5_3.upgrade(data)

    benchmark.pedantic(
        validate_files,
        args=(files,),
        rounds=5,
        iterations=1,
    )


@pytest.mark.benchmark(group="prepare-file")
@pytest.mark.parametrize("file_subset", FILE_SUBSETS)
def test_prepare_file_data(
    benchmark, cleanup_submission_files, file_subset
):  # noqa: ARG001
    """Benchmark file preparation with different file counts."""
    all_files = _load_submission_files(SUBMISSIONS_DIR)
    files = _get_file_subset(all_files, file_subset)

    assert len(files) > 0, "No submissions found"

    def prepare_files(
        files: list[os.DirEntry[str]], trees_names: dict[str, str]
    ) -> None:
        for file in files:
            file_metadata: SubmissionFileMetadata = {
                "path": file.path,
                "name": file.name,
                "size": file.stat().st_size,
            }

            prepare_file_data(file_metadata, trees_names)

    benchmark.pedantic(
        prepare_files,
        args=(
            files,
            trees_names,
        ),
        rounds=5,
        iterations=1,
    )

    files_per_second = len(files) / benchmark.stats.stats.mean

    benchmark.extra_info["files_processed"] = len(files)
    benchmark.extra_info["file_subset"] = file_subset
    benchmark.extra_info["files_per_second"] = f"{files_per_second:.2f}"


def _prepare_buffers(
    files: list[os.DirEntry[str]], trees_names: dict[str, str]
) -> tuple[list, dict[str, list[Any]]]:
    """
    Prepare object buffers from submission files.

    Returns:
        A tuple containing an empty list and a dictionary with buffered objects
        organized by type (issues, checkouts, builds, tests, incidents)
    """
    objects_buffers: dict[str, list[Any]] = {
        "issues": [],
        "checkouts": [],
        "builds": [],
        "tests": [],
        "incidents": [],
    }

    for file in files:
        file_metadata: SubmissionFileMetadata = {
            "path": file.path,
            "name": file.name,
            "size": file.stat().st_size,
        }

        data, metadata = prepare_file_data(file_metadata, trees_names)

        if not data:
            continue

        instances = build_instances_from_submission(data, MAP_TABLENAMES_TO_COUNTER)

        objects_buffers["issues"].extend(instances["issues"])
        objects_buffers["checkouts"].extend(instances["checkouts"])
        objects_buffers["builds"].extend(instances["builds"])
        objects_buffers["tests"].extend(instances["tests"])
        objects_buffers["incidents"].extend(instances["incidents"])

    return [], {
        "issues_buf": objects_buffers["issues"],
        "checkouts_buf": objects_buffers["checkouts"],
        "builds_buf": objects_buffers["builds"],
        "tests_buf": objects_buffers["tests"],
        "incidents_buf": objects_buffers["incidents"],
    }


@pytest.mark.django_db(transaction=True)
@pytest.mark.benchmark(group="flush-buffers")
@pytest.mark.parametrize("file_subset", FILE_SUBSETS)
def test_flush_buffers_perf(benchmark, cleanup_submission_files, file_subset):
    """Benchmark buffer flushing with different file counts (data volumes)."""
    all_files = _load_submission_files(SUBMISSIONS_DIR)
    files = _get_file_subset(all_files, file_subset)

    assert len(files) > 0, "No submissions found"

    benchmark.pedantic(
        flush_buffers,
        setup=lambda: _prepare_buffers(files, trees_names),
        rounds=5,
        iterations=1,
    )

    files_per_second = len(files) / benchmark.stats.stats.mean

    benchmark.extra_info["files_processed"] = len(files)
    benchmark.extra_info["file_subset"] = file_subset
    benchmark.extra_info["files_per_second"] = f"{files_per_second:.2f}"


@pytest.mark.parametrize("batch_size", BATCH_SIZES)
@pytest.mark.benchmark(group="ingest-parallel-batch-size")
def test_ingest_parallel_batch_size(
    benchmark, cleanup_submission_files, batch_size
):  # noqa: ARG001
    all_files = _load_submission_files(SUBMISSIONS_DIR)
    files = _get_file_subset(all_files, 1000)

    assert len(files) > 0, "No submissions found"

    with patch(
        "kernelCI_app.management.commands.helpers.kcidbng_ingester.INGEST_BATCH_SIZE",
        batch_size,
    ):
        benchmark.pedantic(
            ingest_submissions_parallel,
            args=(
                files,
                trees_names,
                os.path.join(SUBMISSIONS_DIR, "archive"),
                os.path.join(SUBMISSIONS_DIR, "failed"),
                1,
            ),
            rounds=5,
            iterations=1,
            teardown=_restore_submission_files,
        )

    files_per_second = len(files) / benchmark.stats.stats.mean

    benchmark.extra_info["files_processed"] = len(files)
    benchmark.extra_info["batch_size"] = batch_size
    benchmark.extra_info["files_per_second"] = f"{files_per_second:.2f}"


@pytest.mark.benchmark(group="build-instances")
@pytest.mark.parametrize("file_subset", FILE_SUBSETS)
def test_build_instances_perf(benchmark, cleanup_submission_files, file_subset):
    """Benchmark building instances from submission data."""
    all_files = _load_submission_files(SUBMISSIONS_DIR)
    files = _get_file_subset(all_files, file_subset)

    assert len(files) > 0, "No submissions found"

    data_list = []
    for file in files:
        file_metadata: SubmissionFileMetadata = {
            "path": file.path,
            "name": file.name,
            "size": file.stat().st_size,
        }

        data, _ = prepare_file_data(file_metadata, trees_names)
        if data:
            data_list.append(data)

    # Calculate total items to be processed
    total_items = 0
    for data in data_list:
        instances = build_instances_from_submission(data, MAP_TABLENAMES_TO_COUNTER)
        for key in instances:
            total_items += len(instances[key])

    def run_build_instances(data_list):
        for data in data_list:
            build_instances_from_submission(data, MAP_TABLENAMES_TO_COUNTER)

    benchmark.pedantic(
        run_build_instances,
        args=(data_list,),
        rounds=5,
        iterations=1,
    )

    items_per_second = total_items / benchmark.stats.stats.mean

    benchmark.extra_info["items_processed"] = total_items
    benchmark.extra_info["file_subset"] = file_subset
    benchmark.extra_info["items_per_second"] = f"{items_per_second:.2f}"
