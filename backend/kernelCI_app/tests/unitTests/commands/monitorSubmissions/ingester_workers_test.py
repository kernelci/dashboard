import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from kernelCI_app.management.commands.helpers import kcidbng_ingester as ingester


def prepare(file, trees):
    return {"name": file["name"]}, {}


def instances(data, counters):
    return {
        "issues": [SimpleNamespace(id=data["name"])],
        "checkouts": [],
        "builds": [],
        "tests": [],
        "incidents": [],
    }


def flush(**kwargs):
    """Replace only database writes; preserve buffer and archive behavior."""
    if not kwargs["issues_buf"]:
        return
    with kwargs["counter_lock"]:
        kwargs["stat_ok"].value += len(kwargs["buffer_files"])
    for name, path in kwargs["buffer_files"]:
        Path(path).rename(Path(kwargs["dirs"]["archive"]) / name)
    kwargs["issues_buf"].clear()
    kwargs["buffer_files"].clear()


def make_files(root, prefix, count):
    files = []
    for n in range(count):
        path = root / f"{prefix}-{n}.json"
        path.write_text("{}")
        files.append(str(path))
    return files


@pytest.fixture
def worker_io(tmp_path):
    dirs = {}
    for name in ("archive", "failed", "pending_retry"):
        path = tmp_path / name
        path.mkdir()
        dirs[name] = str(path)
    with (
        patch.object(ingester, "prepare_file_data", prepare),
        patch.object(ingester, "build_instances_from_submission", instances),
        patch.object(ingester, "flush_buffers", flush),
        patch.object(ingester, "INGEST_QUEUE_MAXSIZE", 1),
        patch.object(ingester, "INGEST_FILES_BATCH_SIZE", 2),
    ):
        yield dirs


def test_reuses_workers_and_flushes_partial_batches_each_cycle(tmp_path, worker_io):
    with ingester.IngestionWorkers({}, worker_io, 2) as workers:
        pids = [writer.pid for writer in workers.writers]
        for cycle in range(3):
            files = make_files(tmp_path, str(cycle), 5)
            workers.ingest(files)
            assert workers.processed.value == workers.stat_ok.value == 5
            assert workers.stat_fail.value == 0
            assert all(not Path(path).exists() for path in files)
            assert len(list(Path(worker_io["archive"]).iterdir())) == (cycle + 1) * 5
            assert [writer.pid for writer in workers.writers] == pids
            assert all(writer.is_alive() for writer in workers.writers)
        workers.ingest([])
        assert workers.processed.value == workers.stat_ok.value == 0
    assert all(writer.exitcode == 0 for writer in workers.writers)


@pytest.mark.parametrize("stage", ["prepare", "instances"])
def test_bad_file_is_moved_to_failed_and_the_worker_survives(
    tmp_path, worker_io, stage
):
    def prepare_or_raise(file, trees):
        if file["name"].startswith("bad"):
            raise ValueError("poison")
        return prepare(file, trees)

    def instances_or_raise(data, counters):
        if data["name"].startswith("bad"):
            raise ValueError("poison")
        return instances(data, counters)

    target, failure = (
        ("prepare_file_data", prepare_or_raise)
        if stage == "prepare"
        else ("build_instances_from_submission", instances_or_raise)
    )
    good = make_files(tmp_path, "good", 3)
    bad = make_files(tmp_path, "bad", 1)
    with (
        patch.object(ingester, target, failure),
        ingester.IngestionWorkers({}, worker_io, 2) as workers,
    ):
        pids = [writer.pid for writer in workers.writers]
        workers.ingest(good + bad)
        assert workers.processed.value == 4
        assert workers.stat_ok.value == 3
        assert workers.stat_fail.value == 1
        assert (Path(worker_io["failed"]) / "bad-0.json").exists()
        assert all(not Path(path).exists() for path in good)
        assert [writer.pid for writer in workers.writers] == pids

        workers.ingest(make_files(tmp_path, "next", 2))
        assert workers.stat_ok.value == 2
    assert all(writer.exitcode == 0 for writer in workers.writers)


def test_pipe_errors_inside_ingestion_are_reported_as_failures(tmp_path, worker_io):
    def broken_batch(*args):
        raise BrokenPipeError("not the control pipe")

    with (
        patch.object(ingester, "process_batch", broken_batch),
        patch.object(ingester, "WORKER_FAILURES_COUNTER") as failures,
    ):
        with pytest.raises(RuntimeError, match="restart required"):
            with ingester.IngestionWorkers({}, worker_io, 1) as workers:
                workers.ingest(make_files(tmp_path, "pipe", 2))
        failures.labels.assert_called_once_with(ingester="django", reason="exception")
    # The traceback reached the exit code instead of being swallowed as parent loss.
    assert workers.writers[0].exitcode == 1


def crash(file, trees):
    os._exit(9)


@pytest.mark.parametrize("stage", ["prepare", "flush"])
def test_worker_crash_aborts_and_leaves_files_for_retry(tmp_path, worker_io, stage):
    files = make_files(tmp_path, "crash", 20)

    def crash_on_flush(**kwargs):
        if kwargs["issues_buf"]:
            os._exit(9)

    target, failure = (
        ("prepare_file_data", crash)
        if stage == "prepare"
        else ("flush_buffers", crash_on_flush)
    )
    with (
        patch.object(ingester, target, failure),
        patch.object(ingester, "WORKER_FAILURES_COUNTER") as failures,
    ):
        with pytest.raises(RuntimeError, match="restart required"):
            with ingester.IngestionWorkers({}, worker_io, 2) as workers:
                workers.ingest(files)
        failures.labels.assert_any_call(ingester="django", reason="exception")
    assert all(not writer.is_alive() for writer in workers.writers)
    assert all(Path(path).exists() for path in files)


def test_dead_idle_worker_aborts_before_next_cycle(tmp_path, worker_io):
    with patch.object(ingester, "WORKER_FAILURES_COUNTER") as failures:
        with pytest.raises(RuntimeError, match="restart required"):
            with ingester.IngestionWorkers({}, worker_io, 2) as workers:
                lost = workers.writers[0]
                lost.kill()
                lost.join(timeout=5)
                workers.ingest(make_files(tmp_path, "idle", 3))
        failures.labels.assert_called_once_with(ingester="django", reason="signal")
    assert all(not writer.is_alive() for writer in workers.writers)


def abandoned_lock_probe(root, lock_name):
    root = Path(root)
    dirs = {name: str(root / name) for name in ("archive", "failed", "pending_retry")}
    for path in dirs.values():
        Path(path).mkdir()
    files = make_files(root, "retry", 3)

    def die_holding_lock(*args):
        lock = args[-1] if lock_name == "counter" else args[0]._rlock
        lock.acquire()
        os._exit(9)

    with patch.object(ingester, "process_batch", die_holding_lock):
        with pytest.raises(RuntimeError, match="restart required"):
            with ingester.IngestionWorkers({}, dirs, 2) as workers:
                workers.ingest(files)
    assert all(not writer.is_alive() for writer in workers.writers)
    assert all(Path(path).exists() for path in files)

    # A supervisor restart constructs a fresh group and can retry the files.
    with (
        patch.object(ingester, "prepare_file_data", prepare),
        patch.object(ingester, "build_instances_from_submission", instances),
        patch.object(ingester, "flush_buffers", flush),
        ingester.IngestionWorkers({}, dirs, 2) as restarted,
    ):
        restarted.ingest(files)
        assert restarted.stat_ok.value == len(files)
        assert not any(Path(path).exists() for path in files)


@pytest.mark.parametrize("lock_name", ["counter", "queue"])
def test_abandoned_locks_abort_and_fresh_workers_can_retry(tmp_path, lock_name):
    module = (
        "kernelCI_app.tests.unitTests.commands.monitorSubmissions.ingester_workers_test"
    )
    process = subprocess.Popen(  # noqa: S603 - local interpreter and test-owned paths
        [
            sys.executable,
            "-c",
            f"import django; django.setup(); from {module} import abandoned_lock_probe; "
            f"abandoned_lock_probe({str(tmp_path)!r}, {lock_name!r})",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    try:
        output, _ = process.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        # A regression must fail the test rather than leave hung workers behind.
        os.killpg(process.pid, signal.SIGKILL)
        output, _ = process.communicate(timeout=5)
        pytest.fail(f"abandoned {lock_name} lock stalled ingestion: {output}")
    assert process.returncode == 0, output


def test_idle_workers_exit_when_parent_control_pipes_close(worker_io):
    with ingester.IngestionWorkers({}, worker_io, 2) as workers:
        workers.ingest([])
        for control in workers.controls:
            control.close()
        for writer in workers.writers:
            writer.join(timeout=5)
            assert writer.exitcode == 0


def test_each_worker_cleans_its_log_cache_between_cycles(worker_io):
    from kernelCI_app.management.commands.helpers import log_excerpt_utils as logs

    process_batch = ingester.process_batch

    def cached_batch(*args):
        assert not logs.CACHE_LOGS, "previous cycle's oversized cache was retained"
        logs.CACHE_LOGS["entry"] = "url"
        process_batch(*args)

    with (
        patch.dict(logs.CACHE_LOGS, clear=True),
        patch.object(logs, "CACHE_LOGS_SIZE_LIMIT", 0),
        patch.object(ingester, "process_batch", cached_batch),
        ingester.IngestionWorkers({}, worker_io, 2) as workers,
    ):
        workers.ingest([])
        workers.ingest([])


def test_interrupt_kills_workers_that_ignore_termination(worker_io):
    with pytest.raises(KeyboardInterrupt):
        with ingester.IngestionWorkers({}, worker_io, 2) as workers:
            # A completed empty cycle confirms both children installed
            # their signal handlers before testing termination.
            workers.ingest([])
            raise KeyboardInterrupt
    assert all(writer.exitcode == -signal.SIGKILL for writer in workers.writers)


def test_workers_survive_a_group_wide_sigterm(tmp_path, worker_io):
    with ingester.IngestionWorkers({}, worker_io, 2) as workers:
        workers.ingest([])
        pids = [writer.pid for writer in workers.writers]
        for pid in pids:
            os.kill(pid, signal.SIGTERM)
        workers.ingest(make_files(tmp_path, "term", 4))
        assert workers.stat_ok.value == 4
        assert [writer.pid for writer in workers.writers] == pids
    assert all(writer.exitcode == 0 for writer in workers.writers)


def orphan_probe(root):
    """Leave workers waiting for batches of a cycle the parent never finishes."""
    root = Path(root)
    dirs = {name: str(root / name) for name in ("archive", "failed", "pending_retry")}
    for path in dirs.values():
        Path(path).mkdir()
    with ingester.IngestionWorkers({}, dirs, 2) as workers:
        for control in workers.controls:
            control.send(True)
        print(json.dumps([writer.pid for writer in workers.writers]), flush=True)
        signal.pause()


def process_state(pid):
    try:
        with open(f"/proc/{pid}/status") as status:
            for line in status:
                if line.startswith("State:"):
                    return line.split()[1]
    except FileNotFoundError:
        return None


def test_workers_exit_when_parent_dies_mid_cycle(tmp_path):
    module = (
        "kernelCI_app.tests.unitTests.commands.monitorSubmissions.ingester_workers_test"
    )
    parent = subprocess.Popen(  # noqa: S603 - local interpreter and test-owned paths
        [
            sys.executable,
            "-c",
            f"import django; django.setup(); from {module} import orphan_probe; "
            f"orphan_probe({str(tmp_path)!r})",
        ],
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        pids = json.loads(parent.stdout.readline())
    finally:
        parent.kill()
        parent.wait(timeout=10)
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if all(process_state(pid) in (None, "Z") for pid in pids):
            return
        time.sleep(0.2)
    pytest.fail(f"orphaned workers still running: {pids}")


def metrics_probe(root):
    """Run in a fresh interpreter so multiprocess metrics activate on import."""
    from prometheus_client import CollectorRegistry, Gauge, Histogram, generate_latest
    from prometheus_client.multiprocess import MultiProcessCollector

    from kernelCI_app.management.commands import monitor_submissions as monitor

    root = Path(root)
    dirs = {name: str(root / name) for name in ("archive", "failed", "pending_retry")}
    for path in dirs.values():
        Path(path).mkdir()
    metric_dir = Path(os.environ["PROMETHEUS_MULTIPROC_DIR"])
    histogram = Histogram("probe_seconds", "Probe timing")
    gauge = Gauge("probe_active", "Probe gauge", multiprocess_mode="livemax")

    process_batch = ingester.process_batch

    def measured_batch(*args):
        histogram.observe(0.1)
        gauge.set(1)
        # Exercise every metric type even if this worker receives no files.
        ingester.FILES_INGESTER_COUNTER.labels(ingester="django").inc(0)
        return process_batch(*args)

    registry = CollectorRegistry()
    MultiProcessCollector(registry)
    command = monitor.Command()
    counts, scrape_seconds = [], []
    with (
        patch.object(ingester, "prepare_file_data", prepare),
        patch.object(ingester, "process_batch", measured_batch),
        patch.object(ingester, "build_instances_from_submission", instances),
        patch.object(ingester, "flush_buffers", flush),
        patch.object(ingester, "INGEST_FILES_BATCH_SIZE", 1),
        ingester.IngestionWorkers({}, dirs, 2) as workers,
    ):
        pids = [writer.pid for writer in workers.writers]
        for cycle in range(20):
            workers.ingest(make_files(root, str(cycle), 8))
            command._last_metrics_scan = float("-inf")
            command._update_prometheus_file_count()
            counts.append(len(list(metric_dir.glob("*.db"))))
            start = time.monotonic()
            payload = generate_latest(registry).decode()
            scrape_seconds.append(time.monotonic() - start)
            assert (
                f'kcidb_ingestions_total{{ingester="django"}} {float((cycle + 1) * 8)}'
                in payload
            )
            assert (
                f'kcidb_ingester_prometheus_files{{ingester="django"}} {float(counts[-1])}'
                in payload
            )
            assert [writer.pid for writer in workers.writers] == pids
        assert len(set(counts)) == 1, counts
    for pid in pids:
        assert not (metric_dir / f"gauge_livemax_{pid}.db").exists()
        assert (metric_dir / f"counter_{pid}.db").exists()
    payload = generate_latest(registry).decode()
    assert 'kcidb_ingestions_total{ingester="django"} 160.0' in payload
    print(
        json.dumps({"file_counts": counts, "max_scrape_seconds": max(scrape_seconds)})
    )


def test_metrics_files_remain_bounded_and_totals_survive_shutdown(tmp_path):
    metrics = tmp_path / "metrics"
    metrics.mkdir()
    module = (
        "kernelCI_app.tests.unitTests.commands.monitorSubmissions.ingester_workers_test"
    )
    result = subprocess.run(  # noqa: S603 - local interpreter and test-owned paths
        [
            sys.executable,
            "-c",
            f"import django; django.setup(); from {module} import metrics_probe; "
            f"metrics_probe({str(tmp_path)!r})",
        ],
        env={**os.environ, "PROMETHEUS_MULTIPROC_DIR": str(metrics)},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    print(result.stdout.splitlines()[-1])
