from kernelCI_app.management.commands.helpers.kcidbng_ingester import (
    ingest_submissions_parallel,
)
import pytest
import os
import shutil
import zipfile
import glob

trees_names = {
    "mainline": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
}

SUBMISSIONS_DIR = "tests_submissions"
SUBMISSIONS_BACKUP_DIR = "tests_submissions_backup"
SUBMISSIONS_ZIP = os.path.join(SUBMISSIONS_DIR, "submissions.zip")


def load_submission_files(dir_path: str) -> list[os.DirEntry[str]]:
    with os.scandir(dir_path) as it:
        return [
            entry for entry in it if entry.is_file() and entry.name.endswith(".json")
        ]


def restore_submission_files(*args, **kwargs) -> None:
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


def unzip_submissions():
    """Unzip submissions.zip if it exists."""
    if os.path.exists(SUBMISSIONS_ZIP):
        with zipfile.ZipFile(SUBMISSIONS_ZIP, "r") as zip_ref:
            zip_ref.extractall(SUBMISSIONS_DIR)


def delete_json_files():
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
    unzip_submissions()

    if os.path.exists(SUBMISSIONS_DIR):
        shutil.copytree(SUBMISSIONS_DIR, SUBMISSIONS_BACKUP_DIR, dirs_exist_ok=True)

    yield

    if os.path.exists(SUBMISSIONS_BACKUP_DIR):
        if os.path.exists(SUBMISSIONS_DIR):
            shutil.rmtree(SUBMISSIONS_DIR)
        shutil.copytree(SUBMISSIONS_BACKUP_DIR, SUBMISSIONS_DIR)
        shutil.rmtree(SUBMISSIONS_BACKUP_DIR)

    delete_json_files()


@pytest.mark.django_db(transaction=True)
def test_ingest_perf(benchmark, cleanup_submission_files):  # noqa: ARG001
    """Benchmark ingestion performance with pytest-benchmark."""
    files = load_submission_files(SUBMISSIONS_DIR)

    assert len(files) > 0, "No submissions found"

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
        teardown=restore_submission_files,
    )

    files_per_second = len(files) / benchmark.stats.stats.mean

    benchmark.extra_info["files_processed"] = len(files)
    benchmark.extra_info["files_per_second"] = f"{files_per_second:.2f}"

    assert (
        benchmark.stats.stats.mean < 10
    ), f"Ingestion took {benchmark.stats.stats.mean:.2f}s average, expected less than 10s"
