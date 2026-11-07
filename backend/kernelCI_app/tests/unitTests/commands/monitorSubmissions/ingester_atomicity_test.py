"""Exercise real workers and flushes with a local transactional persistence stub.

SQLite replaces the PostgreSQL write helpers, not the ingestion/archival logic.
These checks cover commit/rollback and process death, not PostgreSQL SQL or locks.
"""

import json
import multiprocessing
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

from kernelCI_app.management.commands.helpers import kcidbng_ingester as ingester
from kernelCI_app.management.commands.helpers.file_utils import sweep_pending_retry

TABLES = ("issues", "checkouts", "builds", "tests", "incidents")


class Persistence:
    """Durable test writes with explicit transaction and archive failure points."""

    def __init__(self, root):
        self.dirs = {
            name: str(root / name) for name in ("archive", "failed", "pending_retry")
        }
        for directory in self.dirs.values():
            Path(directory).mkdir()
        self.database = root / "records.sqlite"
        with sqlite3.connect(self.database) as db:
            db.execute(
                "CREATE TABLE records (kind TEXT, id TEXT, PRIMARY KEY (kind, id))"
            )
        db.close()
        self.fail = None
        self.boundary = lambda stage: None
        self.connection = None
        self.rename = os.rename

    @contextmanager
    def atomic(self):
        self.connection = sqlite3.connect(self.database)
        try:
            with self.connection:
                yield
                self.boundary("before_commit")
                if self.fail == "commit":
                    raise RuntimeError("commit failed")
            self.boundary("after_commit")
        finally:
            self.connection.close()

    def consume(self, buffer, table):
        if self.fail == table:
            raise RuntimeError(f"{table} write failed")
        self.connection.executemany(
            "INSERT INTO records VALUES (?, ?) ON CONFLICT DO NOTHING",
            [(table, item.id) for item in buffer],
        )

    def aggregate(self, **kwargs):
        if self.fail == "aggregate":
            raise RuntimeError("aggregation failed")
        for table, items in kwargs.items():
            self.consume(items, table)

    def archive(self, source, destination):
        is_archive = Path(destination).parent == Path(self.dirs["archive"])
        if self.fail == "archive" and is_archive:
            raise OSError("archive unavailable")
        self.rename(source, destination)
        if is_archive:
            self.boundary("after_archive")

    def read_records(self):
        with sqlite3.connect(self.database) as db:
            rows = set(db.execute("SELECT kind, id FROM records"))
        db.close()
        return rows


@pytest.fixture
def persistence(tmp_path, monkeypatch):
    state = Persistence(tmp_path)

    def prepare(file, trees):
        return json.loads(Path(file["path"]).read_text()), {}

    def instances(data, counters):
        return {
            table: [SimpleNamespace(id=id) for id in data[table]] for table in TABLES
        }

    monkeypatch.setattr(ingester, "prepare_file_data", prepare)
    monkeypatch.setattr(ingester, "build_instances_from_submission", instances)
    monkeypatch.setattr(ingester.transaction, "atomic", state.atomic)
    monkeypatch.setattr(ingester, "assign_lab_ids", lambda *args: None)
    monkeypatch.setattr(ingester, "consume_buffer", state.consume)
    monkeypatch.setattr(ingester, "aggregate_checkouts_and_pendings", state.aggregate)
    monkeypatch.setattr(ingester.os, "rename", state.archive)
    monkeypatch.setattr(ingester, "INGEST_BATCH_SIZE", 2)
    monkeypatch.setattr(ingester, "INGEST_FILES_BATCH_SIZE", 1)
    monkeypatch.setattr(ingester, "INGEST_QUEUE_MAXSIZE", 1)
    return state


def submission(root, name, threshold_table=None, empty=False):
    data = {
        table: []
        if empty
        else [f"{name}-{n}" for n in range(2 if table == threshold_table else 1)]
        for table in TABLES
    }
    path = root / f"{name}.json"
    path.write_text(json.dumps(data))
    expected = {(table, id) for table, ids in data.items() for id in ids}
    for table, aggregate in (
        ("checkouts", "checkouts_instances"),
        ("builds", "build_instances"),
        ("tests", "tests_instances"),
    ):
        expected.update((aggregate, id) for id in data[table])
    return str(path), expected


@pytest.mark.parametrize("threshold_table", [*TABLES, None])
def test_archived_submissions_include_every_table_and_aggregate(
    tmp_path, persistence, threshold_table
):
    expected = set()
    with ingester.IngestionWorkers({}, persistence.dirs, 1) as workers:
        pid = workers.writers[0].pid
        for cycle in range(2):
            files = []
            for index in range(3):
                path, rows = submission(tmp_path, f"{cycle}-{index}", threshold_table)
                files.append(path)
                expected.update(rows)
            workers.ingest(files)
            assert workers.stat_ok.value == 3
            assert workers.stat_fail.value == 0
            assert persistence.read_records() == expected
            assert all(
                (Path(persistence.dirs["archive"]) / Path(path).name).exists()
                for path in files
            )
            assert workers.writers[0].pid == pid


def test_valid_submission_without_records_is_archived(tmp_path, persistence):
    path, _ = submission(tmp_path, "empty", empty=True)
    with ingester.IngestionWorkers({}, persistence.dirs, 1) as workers:
        workers.ingest([path])
        assert workers.stat_ok.value == 1
        assert workers.stat_fail.value == 0
    assert (Path(persistence.dirs["archive"]) / "empty.json").exists()
    assert not Path(path).exists()
    assert persistence.read_records() == set()


@pytest.mark.parametrize("stage", ["incidents", "aggregate", "commit", "archive"])
def test_failed_flush_can_retry_complete_submissions(tmp_path, persistence, stage):
    path, expected = submission(tmp_path, "retry", "issues")
    persistence.fail = stage
    with ingester.IngestionWorkers({}, persistence.dirs, 1) as workers:
        workers.ingest([path])
        assert workers.stat_ok.value == 0
        assert workers.stat_fail.value == 1
    assert not (Path(persistence.dirs["archive"]) / "retry.json").exists()
    assert (Path(persistence.dirs["pending_retry"]) / "retry.json").exists()
    assert persistence.read_records() == (expected if stage == "archive" else set())

    persistence.fail = None
    assert (
        sweep_pending_retry(str(tmp_path), persistence.dirs["pending_retry"], 10) == 1
    )
    with ingester.IngestionWorkers({}, persistence.dirs, 1) as workers:
        workers.ingest([path])
        assert workers.stat_ok.value == 1
    assert persistence.read_records() == expected
    assert (Path(persistence.dirs["archive"]) / "retry.json").exists()


@pytest.mark.parametrize("stage", ["before_commit", "after_commit", "after_archive"])
def test_sibling_crash_preserves_complete_or_retryable_submissions(
    tmp_path, persistence, monkeypatch, stage
):
    path, expected = submission(tmp_path, "survivor", "issues")
    crash_path = tmp_path / "crash.json"
    crash_path.write_text("{}")
    context = multiprocessing.get_context("fork")
    reached_boundary = context.Event()
    release = context.Event()

    def hold_at_boundary(boundary):
        if boundary == stage:
            reached_boundary.set()
            # The parent should kill this worker before it can continue.
            if not release.wait(timeout=10):
                raise RuntimeError("worker was not killed at the requested boundary")

    prepare = ingester.prepare_file_data

    def prepare_or_crash(file, trees):
        if file["path"] == str(crash_path):
            if not reached_boundary.wait(timeout=10):
                os._exit(8)
            os._exit(9)
        return prepare(file, trees)

    persistence.boundary = hold_at_boundary
    with monkeypatch.context() as patch:
        patch.setattr(ingester, "prepare_file_data", prepare_or_crash)
        with pytest.raises(RuntimeError, match="restart required"):
            with ingester.IngestionWorkers({}, persistence.dirs, 2) as workers:
                workers.ingest([path, str(crash_path)])
    assert reached_boundary.is_set()
    assert sorted(writer.exitcode for writer in workers.writers) == [-9, 9]
    assert persistence.read_records() == (
        set() if stage == "before_commit" else expected
    )
    archived = Path(persistence.dirs["archive"]) / "survivor.json"
    assert archived.exists() == (stage == "after_archive")
    assert Path(path).exists() == (stage != "after_archive")

    # Restart uses fresh queues/locks and retries only unarchived submissions.
    persistence.boundary = lambda boundary: None
    with ingester.IngestionWorkers({}, persistence.dirs, 1) as restarted:
        restarted.ingest([path] if Path(path).exists() else [])
    assert persistence.read_records() == expected
    assert archived.exists()
