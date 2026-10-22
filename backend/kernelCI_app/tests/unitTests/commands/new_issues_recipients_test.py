import os
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.conf import settings

from kernelCI_app.management.commands.notifications import look_for_new_issues
from kernelCI_app.typeModels.notificationRecipients import (
    NEW_ISSUES_FOLDER,
    RecipientFileError,
    load_new_issue_files,
)

MODULE = "kernelCI_app.management.commands.notifications"
SOUND_URL = "https://git.kernel.org/pub/scm/linux/kernel/git/broonie/sound.git"
WHEN = datetime(2026, 10, 22, 12, 0, tzinfo=timezone.utc)
DEFAULT_YAML = "to: kernelci-results@groups.io\nissues: [build, boot]\n"
SOUND_SUBSCRIPTION = f"broonie-sound:\n  url: {SOUND_URL}\n"


def write_new_issues(tmp_path, files, subscriptions=None):
    base = tmp_path / "notifications"
    (base / "subscriptions").mkdir(parents=True)
    (base / "new_issues").mkdir()
    for name, content in (subscriptions or {}).items():
        (base / "subscriptions" / name).write_text(content)
    for name, content in files.items():
        (base / "new_issues" / name).write_text(content)
    return str(base / "new_issues")


def _issue(**overrides):
    issue = {
        "id": "issue-1",
        "version": 1,
        "build_id": "build-1",
        "test_id": None,
        "origin": "maestro",
        "git_repository_url": SOUND_URL,
        "git_repository_branch": "for-next",
        "platform": None,
        "comment": "broke",
        "_timestamp": WHEN,
        "tree_name": "broonie-sound",
        "git_commit_hash": "abc",
        "incident_count": 1,
    }
    issue.update(overrides)
    return issue


def _email_args(**overrides):
    args = SimpleNamespace(
        send=False,
        yes=True,
        to=None,
        cc=None,
        in_reply_to=None,
        ignore_recipients=False,
        add_mailing_lists=False,
        regression_report=False,
    )
    for key, value in overrides.items():
        setattr(args, key, value)
    return args


def _run(directory, issues, email_args, other=None):
    events = []

    def query(*, include_other_tests=False):
        events.append(("query", include_other_tests))
        if include_other_tests:
            return other or []
        return issues

    def store(rows):
        events.append(("store", [row["id"] for row in rows]))
        return rows

    def send(**kwargs):
        events.append("send")
        return None

    with (
        patch(f"{MODULE}.get_running_instance", return_value=None),
        patch(f"{MODULE}.kcidb_new_issues", side_effect=query),
        patch(f"{MODULE}.exclude_already_found_and_store", side_effect=store),
        patch(f"{MODULE}.send_email_report", side_effect=send) as sent,
        patch(f"{MODULE}.generate_issue_report") as regression,
    ):
        look_for_new_issues(
            service=object(), email_args=email_args, directory=directory
        )
    return events, sent, regression


def test_only_default_yaml_sends_one_community_mail(tmp_path, capsys):
    directory = write_new_issues(tmp_path, {"default.yaml": DEFAULT_YAML})
    build = _issue(id="build-maestro")
    other_origin = _issue(id="build-microsoft", origin="microsoft")
    boot = _issue(id="boot-1", build_id=None, test_id="t1")
    events, sent, regression = _run(
        directory, [build, other_origin, boot], _email_args()
    )

    assert events[0] == ("query", False)
    assert "query" not in [event[0] for event in events[1:] if event != "send"]
    assert sent.call_count == 1
    report = sent.call_args.kwargs["report"]["content"]
    assert "build-maestro" in report
    assert "boot-1" in report
    assert "Copy from" not in report
    assert "Test regressions" not in report
    assert sent.call_args.kwargs["email_args"].to == "kernelci-results@groups.io"
    assert [call.kwargs["issue_id"] for call in regression.call_args_list] == [
        "build-maestro"
    ]
    printed = capsys.readouterr().out
    assert "To: kernelci-results@groups.io" in printed
    assert "issues: build-maestro, build-microsoft, boot-1" in printed


def test_to_overrides_default_yaml(tmp_path):
    directory = write_new_issues(tmp_path, {"default.yaml": DEFAULT_YAML})
    _, sent, _ = _run(
        directory, [_issue(id="build-maestro")], _email_args(to="me@example.com")
    )

    assert sent.call_args.kwargs["email_args"].to == "me@example.com"


def test_tree_boot_copy_skips_other_rows_and_unmatched_address(tmp_path, capsys):
    directory = write_new_issues(
        tmp_path,
        {
            "default.yaml": DEFAULT_YAML,
            "broonie-sound.yaml": (
                "broonie-sound:\n"
                "  - issues: [boot]\n"
                "    recipients: [maintainer@example.com]\n"
                "  - issues: [boot]\n"
                "    branch: other-branch\n"
                "    recipients: [nobody@example.com]\n"
            ),
        },
        {"broonie-sound.yaml": SOUND_SUBSCRIPTION},
    )
    boot_on_tree = _issue(
        id="boot-sound", build_id=None, test_id="t1", platform="board"
    )
    boot_elsewhere = _issue(
        id="boot-other",
        build_id=None,
        test_id="t2",
        git_repository_url="https://example.com/other.git",
    )
    build_on_tree = _issue(id="build-sound")
    _, sent, _ = _run(
        directory, [build_on_tree, boot_on_tree, boot_elsewhere], _email_args()
    )

    assert sent.call_count == 2
    copy = sent.call_args_list[1].kwargs
    assert copy["email_args"].to == "maintainer@example.com"
    assert copy["email_args"].cc is None
    assert copy["email_args"].add_mailing_lists is False
    assert copy["email_args"].ignore_recipients is True
    assert "boot-sound" in copy["report"]["content"]
    assert "boot-other" not in copy["report"]["content"]
    assert "build-sound" not in copy["report"]["content"]
    assert "Copy from: new_issues/broonie-sound.yaml" in copy["report"]["content"]
    assert "nobody@example.com" not in capsys.readouterr().out


def test_platform_matches_boot_and_not_a_build(tmp_path):
    directory = write_new_issues(
        tmp_path,
        {
            "default.yaml": DEFAULT_YAML,
            "qcs6490_hardware.yaml": (
                "qcs6490-rb3gen2:\n  - recipients: [board-owner@example.com]\n"
            ),
        },
        {"qcs6490_hardware.yaml": "qcs6490-rb3gen2:\n  labs: {}\n"},
    )
    boot = _issue(
        id="boot-board",
        build_id=None,
        test_id="t1",
        platform="qcs6490-rb3gen2",
    )
    other_origin = _issue(
        id="boot-microsoft",
        build_id=None,
        test_id="t2",
        origin="microsoft",
        platform="qcs6490-rb3gen2",
    )
    other_platform = _issue(
        id="boot-other",
        build_id=None,
        test_id="t3",
        platform="other-board",
    )
    build = _issue(id="build-board", platform="qcs6490-rb3gen2")
    _, sent, _ = _run(
        directory, [boot, other_origin, other_platform, build], _email_args(send=True)
    )

    copies = [
        call.kwargs
        for call in sent.call_args_list
        if call.kwargs["email_args"].to == "board-owner@example.com"
    ]
    assert len(copies) == 1
    content = copies[0]["report"]["content"]
    assert "boot-board" in content
    assert "boot-microsoft" not in content
    assert "boot-other" not in content
    assert "build-board" not in content


def test_two_files_sharing_an_address_send_one_mail(tmp_path):
    directory = write_new_issues(
        tmp_path,
        {
            "default.yaml": DEFAULT_YAML,
            "boot.yaml": (
                "broonie-sound:\n"
                "  - issues: [boot]\n"
                "    recipients: ['Maintainer <maintainer@example.com>']\n"
            ),
            "test.yaml": (
                "broonie-sound:\n"
                "  - issues: [test]\n"
                "    recipients: [maintainer@example.com]\n"
            ),
        },
        {"broonie-sound.yaml": SOUND_SUBSCRIPTION},
    )
    boot = _issue(id="boot-sound", build_id=None, test_id="t1")
    test_issue = _issue(id="test-sound", build_id=None, test_id="t2")
    _, sent, _ = _run(directory, [boot], _email_args(send=True), other=[test_issue])

    copies = [
        call.kwargs
        for call in sent.call_args_list
        if "maintainer@example.com" in call.kwargs["email_args"].to
    ]
    assert len(copies) == 1
    assert copies[0]["email_args"].to == "Maintainer <maintainer@example.com>"
    content = copies[0]["report"]["content"]
    assert "boot-sound" in content
    assert "test-sound" in content
    assert "Test regressions" in content
    assert "Copy from: new_issues/boot.yaml, new_issues/test.yaml" in content


def test_test_row_never_comes_from_a_build_incident(tmp_path):
    directory = write_new_issues(
        tmp_path,
        {
            "default.yaml": DEFAULT_YAML,
            "broonie-sound.yaml": (
                "broonie-sound:\n"
                "  - issues: [test]\n"
                "    recipients: [maintainer@example.com]\n"
            ),
        },
        {"broonie-sound.yaml": SOUND_SUBSCRIPTION},
    )
    from_build = _issue(id="from-build", build_id="b1", test_id="t-build")
    real_test = _issue(id="real-test", build_id=None, test_id="t-real")
    events, sent, regression = _run(
        directory, [], _email_args(send=True), other=[from_build, real_test]
    )

    assert ("query", True) in events
    stored = [
        event[1] for event in events if isinstance(event, tuple) and event[0] == "store"
    ]
    assert stored == [[], [], ["real-test"]]
    assert events.index(("store", ["real-test"])) < events.index("send")
    content = sent.call_args.kwargs["report"]["content"]
    assert "real-test" in content
    assert "from-build" not in content
    regression.assert_not_called()


def test_ignore_recipients_skips_copies(tmp_path):
    directory = write_new_issues(
        tmp_path,
        {
            "default.yaml": DEFAULT_YAML,
            "broonie-sound.yaml": (
                "broonie-sound:\n"
                "  - issues: [test]\n"
                "    recipients: [maintainer@example.com]\n"
            ),
        },
        {"broonie-sound.yaml": SOUND_SUBSCRIPTION},
    )
    events, sent, _ = _run(
        directory,
        [_issue(id="boot-sound", build_id=None, test_id="t1")],
        _email_args(send=True, ignore_recipients=True),
        other=[_issue(id="test-sound", build_id=None, test_id="t2")],
    )

    assert events[0] == ("query", False)
    assert ("query", True) not in events
    assert sent.call_count == 1
    assert sent.call_args.kwargs["email_args"].to == "kernelci-results@groups.io"


def test_no_new_issues_sends_nothing(tmp_path, capsys):
    directory = write_new_issues(tmp_path, {"default.yaml": DEFAULT_YAML})
    _, sent, regression = _run(directory, [], _email_args())

    sent.assert_not_called()
    regression.assert_not_called()
    assert "No new issues" in capsys.readouterr().out


def test_loader_rejects_architecture(tmp_path):
    directory = write_new_issues(
        tmp_path,
        {
            "default.yaml": DEFAULT_YAML,
            "broonie-sound.yaml": (
                "broonie-sound:\n"
                "  - issues: [boot]\n"
                "    architecture: [arm64]\n"
                "    recipients: [a@example.com]\n"
            ),
        },
        {"broonie-sound.yaml": SOUND_SUBSCRIPTION},
    )

    with pytest.raises(RecipientFileError) as error:
        load_new_issue_files(directory)

    message = str(error.value)
    assert "broonie-sound.yaml" in message
    assert "entry 0" in message
    assert "key 'architecture'" in message


def test_committed_new_issue_files_are_valid():
    directory = os.path.join(settings.BACKEND_DATA_DIR, NEW_ISSUES_FOLDER)

    default, entries = load_new_issue_files(directory)

    assert entries == []
    assert default.to == "kernelci-results@groups.io"
    assert default.issues == ["build", "boot"]
