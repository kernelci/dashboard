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
    send_email_report,
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
    RecipientEntry,
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
    assert load_recipient_default(
        os.path.join(settings.BACKEND_DATA_DIR, "notifications")
    ).to


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


@pytest.mark.parametrize(
    ("incidents", "matches"),
    [
        (
            [
                {"architecture": "arm64", "compiler": "gcc"},
                {"architecture": "x86_64", "compiler": "clang"},
            ],
            False,
        ),
        ([{"architecture": "arm64", "compiler": "clang"}], True),
        ([], False),
    ],
)
def test_build_scope_matches_one_incident(incidents, matches):
    entry = RecipientEntry(
        recipients=["a@example.org"], architecture="arm64", compiler="clang"
    )
    recipients = resolve_regression_recipients(
        build_issue("main"), incidents, entries_by_url={STABLE_URL: [entry]}
    )
    assert recipients == (["a@example.org"] if matches else [])


def test_test_issue_supports_branch_but_not_build_scope(entries_by_url):
    issue = build_issue("linux-6.12.y") | {"build_id": None, "test_id": "test-1"}
    assert resolve_regression_recipients(issue, [], entries_by_url=entries_by_url) == [
        "list@example.org",
        "branch@example.org",
    ]


@pytest.mark.parametrize("key", ["to", "reply_to", "regressions"])
@pytest.mark.parametrize("value", [None, "", "   ", 42])
def test_defaults_require_nonblank_addresses(tmp_path, key, value):
    import yaml

    defaults = dict(
        to="a@example.org", reply_to="b@example.org", regressions="c@example.org"
    )
    if value is None:
        del defaults[key]
    else:
        defaults[key] = value
    (tmp_path / "default.yaml").write_text(yaml.safe_dump(defaults))
    with pytest.raises(RecipientFileError, match=key):
        load_recipient_default(str(tmp_path))


@pytest.mark.parametrize("regression_report", [False, True])
def test_reports_use_shared_defaults(tmp_path, monkeypatch, regression_report):
    directory = tmp_path / "notifications"
    directory.mkdir()
    (directory / "default.yaml").write_text(
        "to: results@example.org\nreply_to: reply@example.org\nregressions: regressions@example.org\n"
    )
    monkeypatch.setattr(settings, "BACKEND_DATA_DIR", str(tmp_path))
    args = SimpleNamespace(
        send=True,
        add_mailing_lists=True,
        regression_report=regression_report,
        ignore_recipients=False,
        cc=None,
        yes=True,
        tree_name="mainline",
        in_reply_to=None,
    )
    with patch(
        "kernelCI_app.management.commands.helpers.common.smtp_send_email"
    ) as send:
        send_email_report(
            service=None, report={"title": "report", "content": "body"}, email_args=args
        )
    assert send.call_args.args[2] == "results@example.org"
    assert send.call_args.args[6] == "reply@example.org"
    assert send.call_args.args[5] == (
        "regressions@example.org" if regression_report else ""
    )
