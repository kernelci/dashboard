"""Run the installed kci-dev CLI against the local Dashboard test API."""

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

API = os.environ.get("DASHBOARD_API", "http://localhost:8001/api/")

ARM64_COMMIT = "a1c24ab822793eb513351686f631bd18952b7870"
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


def _parse_stdout(stdout: str):
    text = stdout.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return ast.literal_eval(text)


def run_kci_dev(settings_file: Path, *args: str):
    cmd = [
        _kci_dev_executable(),
        "--settings",
        str(settings_file),
        "--debug",
        "results",
        *args,
        "--json",
    ]
    proc = subprocess.run(  # noqa: S603
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    # kci-dev exits 0 on an unusable payload, so empty stdout is also a failure.
    assert proc.returncode == 0 and proc.stdout.strip(), (
        f"command: {' '.join(cmd)}\n"
        f"exit code: {proc.returncode}\n"
        f"stdout:\n{proc.stdout}\n"
        f"stderr:\n{proc.stderr}"
    )
    return _parse_stdout(proc.stdout)


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


def test_builds(settings_file: Path) -> None:
    builds = run_kci_dev(settings_file, "builds", *CHECKOUT_ARGS)
    assert builds
    _assert_fields(builds, BUILD_FIELDS)
    assert any(b["id"] == ARM64_BUILD for b in builds)


def test_build(settings_file: Path) -> None:
    build = run_kci_dev(settings_file, "build", "--id", ARM64_BUILD)
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


def test_test(settings_file: Path) -> None:
    listed = run_kci_dev(settings_file, "tests", *CHECKOUT_ARGS)
    test_id = listed[0]["id"]
    test = run_kci_dev(settings_file, "test", "--id", test_id)
    _assert_fields([test], TEST_FIELDS)
    assert test["id"] == test_id
