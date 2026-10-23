import os
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.conf import settings

from kernelCI_app.management.commands.helpers.common import (
    REGRESSION_FOLDER,
    load_regression_files,
    resolve_regression_recipients,
    unscoped_regression_recipients,
)
from kernelCI_app.management.commands.notifications import (
    generate_issue_report,
    generate_test_report,
)
from kernelCI_app.tests.unitTests.commands.fixtures.report_notifications_data import (
    make_boot_issue,
    make_build_issue,
    make_test,
)
from kernelCI_app.typeModels.notificationRecipients import (
    RecipientFileError,
    load_recipient_default,
)

STABLE_URL = "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git"
MODULE = "kernelCI_app.management.commands.notifications"


def write_tree(tmp_path, *, regression: str, subscriptions: dict[str, str] = None):
    """Creates subscriptions/ and regression/ under tmp_path, returns regression/"""
    if subscriptions is None:
        subscriptions = {"stable.yaml": f"stable:\n  url: {STABLE_URL}\n"}
    (tmp_path / "subscriptions").mkdir()
    for name, content in subscriptions.items():
        (tmp_path / "subscriptions" / name).write_text(content)
    (tmp_path / "regression").mkdir()
    (tmp_path / "regression" / "stable.yaml").write_text(regression)
    return str(tmp_path / "regression")


def test_loader_valid(tmp_path):
    directory = write_tree(
        tmp_path,
        regression=(
            "stable:\n"
            "  - recipients: list@example.org\n"
            "  - branch: linux-6.12.y\n"
            "    architecture: [arm64]\n"
            "    issues: [build]\n"
            "    recipients: [Maintainer <m@example.com>]\n"
        ),
    )

    entries = load_regression_files(directory)

    assert list(entries) == [STABLE_URL]
    unscoped, scoped = entries[STABLE_URL]
    assert unscoped.recipients == ["list@example.org"]
    assert unscoped.scope == {}
    assert scoped.recipients == ["Maintainer <m@example.com>"]
    assert scoped.scope == {
        "issues": ["build"],
        "branch": ["linux-6.12.y"],
        "architecture": ["arm64"],
    }


@pytest.mark.parametrize(
    ("entry", "key"),
    [
        ("{recipients: [a@example.org], unknown: x}", "unknown"),
        ("{recipients: [a@example.org], platform: rk3399}", "platform"),
        ("{recipients: [a@example.org], origin: maestro}", "origin"),
        ("{recipients: [a@example.org], issues: [boot]}", "issues"),
        ("{recipients: []}", "recipients"),
    ],
)
def test_loader_rejects_entry(tmp_path, entry, key):
    directory = write_tree(
        tmp_path, regression=f"stable:\n  - recipients: [ok@example.org]\n  - {entry}\n"
    )

    with pytest.raises(RecipientFileError) as error:
        load_regression_files(directory)

    message = str(error.value)
    assert "stable.yaml" in message
    assert "entry 1" in message
    assert f"key '{key}'" in message


def test_loader_rejects_unknown_tree(tmp_path):
    directory = write_tree(
        tmp_path, regression="mainline:\n  - recipients: [a@example.org]\n"
    )

    with pytest.raises(RecipientFileError, match="unknown tree 'mainline'"):
        load_regression_files(directory)


def test_loader_rejects_duplicate_subscription_url(tmp_path):
    directory = write_tree(
        tmp_path,
        regression="stable:\n  - recipients: [a@example.org]\n",
        subscriptions={
            "stable.yaml": f"stable:\n  url: {STABLE_URL}\n",
            "stable-copy.yaml": f"stable-copy:\n  url: {STABLE_URL}\n",
        },
    )

    with pytest.raises(RecipientFileError, match="also used by"):
        load_regression_files(directory)


def test_loader_rejects_hardware_file(tmp_path):
    directory = write_tree(
        tmp_path, regression="stable:\n  - recipients: [a@example.org]\n"
    )
    (tmp_path / "regression" / "board_hardware.yaml").write_text("board: {}\n")

    with pytest.raises(RecipientFileError, match="hardware files are not allowed"):
        load_regression_files(directory)


def test_committed_regression_files_are_valid():
    directory = os.path.join(settings.BACKEND_DATA_DIR, REGRESSION_FOLDER)

    assert load_regression_files(directory)
    assert load_recipient_default(directory).to


@pytest.fixture
def entries_by_url(tmp_path):
    directory = write_tree(
        tmp_path,
        regression=(
            "stable:\n"
            "  - recipients: [list@example.org]\n"
            "  - branch: linux-6.12.y\n"
            "    recipients: [branch@example.org]\n"
            "  - architecture: arm64\n"
            "    recipients: [arm64@example.org, List <LIST@example.org>]\n"
            "  - branch: linux-6.6.y\n"
            "    compiler: clang-17\n"
            "    recipients: [never@example.org]\n"
        ),
    )
    return load_regression_files(directory)


def build_issue(branch: str) -> dict:
    return {
        "build_id": "maestro:1",
        "git_repository_url": STABLE_URL,
        "git_repository_branch": branch,
    }


def test_resolve_branch_match(entries_by_url):
    recipients = resolve_regression_recipients(
        build_issue("linux-6.12.y"),
        [{"architecture": "x86_64"}],
        entries_by_url=entries_by_url,
    )

    assert recipients == ["list@example.org", "branch@example.org"]


def test_resolve_architecture_match_and_dedup(entries_by_url):
    recipients = resolve_regression_recipients(
        build_issue("linux-6.1.y"),
        [{"architecture": "x86_64"}, {"architecture": "arm64"}],
        entries_by_url=entries_by_url,
    )

    assert recipients == ["list@example.org", "arm64@example.org"]


def test_resolve_scoped_entries_need_every_key(entries_by_url):
    recipients = resolve_regression_recipients(
        build_issue("linux-6.6.y"),
        [{"compiler": "gcc-12"}],
        entries_by_url=entries_by_url,
    )

    assert recipients == ["list@example.org"]


def test_resolve_no_match_for_other_tree(entries_by_url):
    issue = build_issue("linux-6.12.y") | {"git_repository_url": "https://other"}

    assert resolve_regression_recipients(issue, [], entries_by_url=entries_by_url) == []


def test_test_report_uses_only_unscoped_entries(entries_by_url):
    recipients = unscoped_regression_recipients(
        STABLE_URL, entries_by_url=entries_by_url
    )

    assert recipients == ["list@example.org"]


@pytest.fixture
def invalid_regression_files(tmp_path, monkeypatch):
    directory = tmp_path / "notifications"
    directory.mkdir()
    write_tree(directory, regression="stable:\n  - recipients: []\n")
    monkeypatch.setattr(settings, "BACKEND_DATA_DIR", str(tmp_path))


@pytest.mark.parametrize("ignore_recipients", [False, True])
@pytest.mark.parametrize("kind", ["build", "boot"])
def test_issue_report_can_ignore_invalid_recipients(
    invalid_regression_files, ignore_recipients, kind, capsys
):
    issue, incidents = make_build_issue() if kind == "build" else make_boot_issue()
    issue.update(
        version=1,
        _timestamp=datetime(2026, 10, 22, tzinfo=timezone.utc),
        build_id="build-1" if kind == "build" else None,
        test_id="test-1" if kind == "boot" else None,
    )
    email_args = SimpleNamespace(send=False, ignore_recipients=ignore_recipients)
    last_test = {
        "id": "last-pass",
        "start_time": issue["_timestamp"],
        "git_commit_hash": "abc",
    }
    with (
        patch(f"{MODULE}.kcidb_issue_details", return_value=[issue]),
        patch(f"{MODULE}.kcidb_build_incidents", return_value=incidents),
        patch(f"{MODULE}.kcidb_test_incidents", return_value=incidents),
        patch(f"{MODULE}.kcidb_last_build_without_issue", return_value=[]),
        patch(f"{MODULE}.kcidb_last_test_without_issue", return_value=[last_test]),
    ):
        if ignore_recipients:
            generate_issue_report(
                service=None, issue_id=issue["id"], email_args=email_args
            )
            assert "DRY RUN" in capsys.readouterr().out
        else:
            with pytest.raises(RecipientFileError, match="recipients"):
                generate_issue_report(
                    service=None, issue_id=issue["id"], email_args=email_args
                )


@pytest.mark.parametrize("ignore_recipients", [False, True])
def test_test_report_can_ignore_invalid_recipients(
    invalid_regression_files, ignore_recipients, capsys
):
    test = make_test()
    test.update(origin="maestro", _timestamp=test["start_time"])
    email_args = SimpleNamespace(send=False, ignore_recipients=ignore_recipients)
    with (
        patch(f"{MODULE}.get_test_details_data", return_value=[test]),
        patch(f"{MODULE}.get_test_status_history", return_value=[]),
    ):
        if ignore_recipients:
            generate_test_report(
                service=None, test_id=test["id"], email_args=email_args
            )
            assert "DRY RUN" in capsys.readouterr().out
        else:
            with pytest.raises(RecipientFileError, match="recipients"):
                generate_test_report(
                    service=None, test_id=test["id"], email_args=email_args
                )
