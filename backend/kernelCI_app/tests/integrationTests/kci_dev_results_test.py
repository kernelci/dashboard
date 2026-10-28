"""Run the installed kci-dev CLI against the local Dashboard test API."""

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

API = os.environ.get("DASHBOARD_API") or (
    os.environ.get("TEST_BASE_URL", "http://localhost:8000/").rstrip("/") + "/api/"
)

ARM64_COMMIT = "a1c24ab822793eb513351686f631bd18952b7870"
ARM64_BASE = "5b4ec6e1eb7603b6d86a172d77efdf75eb741e7e"
ARM64_GITURL = "https://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux.git"
ARM64_BRANCH = "for-kernelci"
ARM64_TREE = "arm64/for-kernelci"
ARM64_BUILD = "maestro:67b62592f7707533c0ff7a99"
ISSUE_ORIGIN = "origin-fake-00000000"
ISSUE_ID = "maestro:2ff8fe94f6d53f39321d4a37fe15801cedc93573"
CHECKOUT_ARGS = (
    "--origin",
    "maestro",
    "--giturl",
    ARM64_GITURL,
    "--branch",
    ARM64_BRANCH,
    "--commit",
    ARM64_COMMIT,
)
TREE_FIELDS = {
    "tree",
    "giturl",
    "latest_commit_hash",
    "latest_commit_name",
    "latest_commit_start_time",
}
BUILD_FIELDS = {
    "id",
    "config",
    "arch",
    "compiler",
    "status",
    "config_url",
    "log",
    "dashboard",
}
TEST_FIELDS = {
    "id",
    "test_path",
    "hardware",
    "compatibles",
    "config",
    "arch",
    "status",
    "start_time",
    "log",
    "dashboard",
}
ISSUE_FIELDS = {
    "id",
    "comment",
    "origin",
    "version",
    "field_timestamp",
    "culprit_code",
    "culprit_tool",
    "culprit_harness",
    "categories",
    "extra",
}
SUMMARY_FIELDS = {"pass", "fail", "inconclusive"}


def _kci_dev_executable() -> str:
    # Do not resolve sys.executable: venv python may symlink to /usr/bin/python3.
    venv_cli = Path(sys.executable).parent / "kci-dev"
    if venv_cli.is_file():
        return str(venv_cli)
    pytest.fail("kci-dev not found; poetry install the backend dev group")


@pytest.fixture(scope="module")
def settings_file(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("kcidev") / "kci-dev.toml"
    path.write_text(f'dashboard_api = "{API}"\n')
    return path


def _run_kci_dev(
    settings_file: Path, args: tuple[str, ...]
) -> subprocess.CompletedProcess:
    cmd = [
        _kci_dev_executable(),
        "--settings",
        str(settings_file),
        "--debug",
        "results",
        *args,
    ]
    return subprocess.run(  # noqa: S603
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def _format_failure(
    cmd_args: tuple[str, ...], proc: subprocess.CompletedProcess
) -> str:
    return (
        f"command: results {' '.join(cmd_args)}\n"
        f"exit code: {proc.returncode}\n"
        f"stdout:\n{proc.stdout}\n"
        f"stderr:\n{proc.stderr}"
    )


def run_kci_dev(settings_file: Path, *args: str, parse=json.loads):
    proc = _run_kci_dev(settings_file, (*args, "--json"))
    # kci-dev exits 0 on an unusable payload, so empty stdout is also a failure.
    assert proc.returncode == 0 and proc.stdout.strip(), _format_failure(args, proc)
    return parse(proc.stdout.strip())


def _assert_fields(rows, fields: set[str]) -> None:
    for row in rows:
        missing = fields - row.keys()
        assert not missing, missing


def test_trees(settings_file: Path) -> None:
    trees = run_kci_dev(settings_file, "trees", "--origin", "maestro", "--days", "35")
    assert trees
    _assert_fields(trees, TREE_FIELDS)
    assert any(t["tree"] == ARM64_TREE for t in trees)


def test_summary(settings_file: Path) -> None:
    summary = run_kci_dev(settings_file, "summary", *CHECKOUT_ARGS)
    for section in ("builds", "boots", "tests"):
        _assert_fields([summary[section]], SUMMARY_FIELDS)
    assert summary["builds"]["pass"] > 0


def test_builds_temporarily_unavailable(settings_file: Path) -> None:
    # The tree builds endpoint is temporarily disabled to prevent memory exhaustion.
    args = ("builds", *CHECKOUT_ARGS, "--json")
    proc = _run_kci_dev(settings_file, args)
    failure = _format_failure(args, proc)
    assert proc.returncode != 0, failure
    assert not proc.stdout.strip(), failure
    assert "status 503" in proc.stderr, failure


def test_build(settings_file: Path) -> None:
    # A single build is printed as a Python repr.
    build = run_kci_dev(
        settings_file, "build", "--id", ARM64_BUILD, parse=ast.literal_eval
    )
    _assert_fields([build], BUILD_FIELDS)
    assert build["id"] == ARM64_BUILD


def test_tests(settings_file: Path) -> None:
    tests = run_kci_dev(settings_file, "tests", *CHECKOUT_ARGS)
    assert tests
    _assert_fields(tests, TEST_FIELDS)


def test_issues(settings_file: Path) -> None:
    issues = run_kci_dev(
        settings_file, "issues", "--origin", ISSUE_ORIGIN, "--days", "5"
    )
    assert issues
    _assert_fields(issues, ISSUE_FIELDS)
    assert any(issue["id"] == ISSUE_ID for issue in issues)


@pytest.fixture
def compare_cli(monkeypatch):
    # TODO: compare and gate call KernelCIClient() with no config, so --settings
    # never reaches them. Check opening a kci-dev PR so they use the dashboard URL
    # from the settings file, like trees/builds/tests. Then drop this subclass and
    # run both commands through run_kci_dev.
    import kcidev.api as api
    from kcidev.api import KernelCIClient
    from kcidev.main import get_cli

    class Client(KernelCIClient):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault("dashboard_api", API)
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(api, "KernelCIClient", Client)
    return get_cli()


def _invoke_comparison(compare_cli, args: list[str]) -> tuple[int, dict]:
    from click.testing import CliRunner

    result = CliRunner().invoke(compare_cli, args)
    report_line = next(
        line for line in reversed(result.output.splitlines()) if line.startswith('{"')
    )
    return result.exit_code, json.loads(report_line)


def _assert_builds_unavailable(code: int, report: dict) -> None:
    # Compare and gate also depend on the disabled tree builds endpoint.
    assert "builds" in report["error"], report
    assert report["incomplete"] is True
    assert code == 2


def test_compare(compare_cli) -> None:
    code, report = _invoke_comparison(
        compare_cli,
        [
            "results",
            "compare",
            "--origin",
            "maestro",
            "--giturl",
            ARM64_GITURL,
            "--branch",
            ARM64_BRANCH,
            ARM64_BASE,
            ARM64_COMMIT,
            "--format",
            "json",
        ],
    )
    _assert_builds_unavailable(code, report)


def test_gate(compare_cli) -> None:
    code, report = _invoke_comparison(
        compare_cli,
        [
            "results",
            "gate",
            "--origin",
            "maestro",
            "--giturl",
            ARM64_GITURL,
            "--branch",
            ARM64_BRANCH,
            "--base",
            ARM64_BASE,
            "--head",
            ARM64_COMMIT,
            "--format",
            "json",
        ],
    )
    _assert_builds_unavailable(code, report)


def test_test(settings_file: Path) -> None:
    listed = run_kci_dev(settings_file, "tests", *CHECKOUT_ARGS)
    test_id = listed[0]["id"]
    # A single test is printed as a Python repr.
    test = run_kci_dev(settings_file, "test", "--id", test_id, parse=ast.literal_eval)
    _assert_fields([test], TEST_FIELDS)
    assert test["id"] == test_id
