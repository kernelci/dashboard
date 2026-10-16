from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

from kernelCI_app.management.commands.notifications import look_for_new_issues
from kernelCI_app.typeModels.notificationSubscriptions import NewIssueSubscriber

MODULE = "kernelCI_app.management.commands.notifications"
WHEN = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)


def _issue(**overrides):
    issue = {
        "id": "issue-1",
        "version": 1,
        "build_id": "build-1",
        "test_id": None,
        "origin": "maestro",
        "git_repository_url": "https://example.com/sound.git",
        "platform": None,
        "comment": "broke the build",
        "_timestamp": WHEN,
        "tree_name": "sound",
        "git_repository_branch": "for-next",
        "git_commit_hash": "abc",
        "incident_count": 1,
    }
    issue.update(overrides)
    return issue


def _email_args(**overrides):
    args = SimpleNamespace(
        send=False,
        yes=True,
        to="kernelci-results@groups.io",
        cc=None,
        in_reply_to=None,
        ignore_recipients=False,
        add_mailing_lists=False,
        regression_report=False,
    )
    for key, value in overrides.items():
        setattr(args, key, value)
    return args


def _run(
    issues,
    subscribers,
    email_args,
    *,
    other_issues=None,
    issue_report_origins=None,
    issue_report_types=None,
):
    def query(*, include_other_tests=False):
        if include_other_tests:
            return other_issues or []
        return issues

    with (
        patch(f"{MODULE}.get_running_instance", return_value=None),
        patch(f"{MODULE}.kcidb_new_issues", side_effect=query) as fetched,
        patch(
            f"{MODULE}.exclude_already_found_and_store", side_effect=lambda rows: rows
        ),
        patch(f"{MODULE}.new_issue_subscribers", return_value=subscribers),
        patch(f"{MODULE}.send_email_report") as send,
        patch(f"{MODULE}.generate_issue_report") as regression,
    ):
        look_for_new_issues(
            service=object(),
            signup_folder="notifications/subscriptions",
            email_args=email_args,
            issue_report_origins=issue_report_origins,
            issue_report_types=issue_report_types,
        )
    return fetched, send, regression


def test_no_new_issues_block_sends_one_community_summary_and_maestro_build_report(
    capsys,
):
    build_issue = _issue(id="build-maestro")
    boot_issue = _issue(
        id="boot-1",
        build_id=None,
        test_id="test-1",
        origin="microsoft",
        git_repository_url="https://example.com/other.git",
    )
    other_origin = _issue(id="build-other", origin="microsoft")
    fetched, send, regression = _run(
        [build_issue, boot_issue, other_origin],
        [],
        _email_args(),
    )

    fetched.assert_called_once_with()
    assert send.call_count == 1
    report = send.call_args.kwargs["report"]
    assert "build-maestro" in report["content"]
    assert "boot-1" in report["content"]
    assert "Test regressions" not in report["content"]
    assert send.call_args.kwargs["email_args"].to == "kernelci-results@groups.io"
    regression.assert_called_once()
    assert regression.call_args.kwargs["issue_id"] == "build-maestro"
    printed = capsys.readouterr().out
    assert "To: kernelci-results@groups.io" in printed
    assert "issues: build-maestro, build-other, boot-1" in printed


def test_boot_in_issues_sends_a_filtered_copy_and_skips_an_empty_one():
    boot_on_tree = _issue(
        id="boot-sound",
        build_id=None,
        test_id="test-1",
        platform="board",
    )
    boot_elsewhere = _issue(
        id="boot-other",
        build_id=None,
        test_id="test-2",
        git_repository_url="https://example.com/other.git",
    )
    build_on_tree = _issue(id="build-sound")
    subscribers = [
        NewIssueSubscriber(
            email="broonie@kernel.org",
            issue_types=frozenset({"boot"}),
            tree_url="https://example.com/sound.git",
        ),
        NewIssueSubscriber(
            email="nobody@example.com",
            issue_types=frozenset({"test"}),
            tree_url="https://example.com/missing.git",
        ),
    ]
    _, send, _ = _run(
        [boot_on_tree, boot_elsewhere, build_on_tree],
        subscribers,
        _email_args(send=True),
    )

    assert send.call_count == 2
    copy = send.call_args_list[1].kwargs
    assert copy["email_args"].to == "broonie@kernel.org"
    assert copy["email_args"].cc is None
    assert copy["email_args"].add_mailing_lists is False
    assert copy["email_args"].ignore_recipients is True
    assert "boot-sound" in copy["report"]["content"]
    assert "boot-other" not in copy["report"]["content"]
    assert "build-sound" not in copy["report"]["content"]


def test_test_subscription_fetches_other_tests_only_for_that_copy():
    test_issue = _issue(
        id="test-1",
        build_id=None,
        test_id="test-1",
        platform="board",
    )
    subscriber = NewIssueSubscriber(
        email="broonie@kernel.org",
        issue_types=frozenset({"test"}),
        tree_url="https://example.com/sound.git",
    )
    fetched, send, regression = _run(
        [],
        [subscriber],
        _email_args(send=True),
        other_issues=[test_issue],
    )

    assert fetched.call_count == 2
    assert fetched.call_args_list[1].kwargs["include_other_tests"] is True
    assert send.call_count == 1
    assert send.call_args.kwargs["email_args"].to == "broonie@kernel.org"
    assert "test-1" in send.call_args.kwargs["report"]["content"]
    assert "Test regressions" in send.call_args.kwargs["report"]["content"]
    regression.assert_not_called()


def test_issue_report_flags_select_origin_and_type():
    issues = [
        _issue(id="build-maestro"),
        _issue(id="boot-maestro", build_id=None, test_id="t1"),
        _issue(id="build-microsoft", origin="microsoft"),
    ]
    _, _, boot_only = _run(
        issues,
        [],
        _email_args(send=True),
        issue_report_origins=["maestro"],
        issue_report_types=["boot"],
    )
    assert [call.kwargs["issue_id"] for call in boot_only.call_args_list] == [
        "boot-maestro"
    ]

    _, _, microsoft_build = _run(
        issues,
        [],
        _email_args(send=True),
        issue_report_origins=["microsoft"],
        issue_report_types=["build"],
    )
    assert [call.kwargs["issue_id"] for call in microsoft_build.call_args_list] == [
        "build-microsoft"
    ]


def test_ignore_recipients_skips_subscription_copies():
    subscriber = NewIssueSubscriber(
        email="broonie@kernel.org",
        issue_types=frozenset({"boot", "test"}),
        tree_url="https://example.com/sound.git",
    )
    fetched, send, _ = _run(
        [_issue(id="boot-sound", build_id=None, test_id="test-1")],
        [subscriber],
        _email_args(send=True, ignore_recipients=True),
    )

    fetched.assert_called_once_with()
    assert send.call_count == 1
    assert send.call_args.kwargs["email_args"].to == "kernelci-results@groups.io"
