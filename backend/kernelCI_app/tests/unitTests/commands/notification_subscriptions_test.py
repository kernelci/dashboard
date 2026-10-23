from pathlib import Path

import pytest
import yaml

from kernelCI_app.management.commands.helpers.summary import (
    process_hardware_submissions_files,
    process_submissions_files,
)
from kernelCI_app.typeModels.notificationSubscriptions import (
    NotificationConfigError,
    cc_addresses,
    load_metrics_rules,
    load_subscriptions,
)

NOTIFICATIONS = Path(__file__).resolve().parents[4] / "data" / "notifications"
SUBSCRIPTIONS = NOTIFICATIONS / "subscriptions"
METRICS = NOTIFICATIONS / "metrics"


def _write(directory: Path, name: str, body: dict) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_text(yaml.safe_dump(body))


def test_subscription_files_load_and_keep_one_cc_address_per_entry():
    trees, hardware = load_subscriptions(SUBSCRIPTIONS)
    assert trees
    assert hardware
    load_metrics_rules(METRICS, trees=trees, hardware=hardware)

    for path in SUBSCRIPTIONS.glob("*.y*ml"):
        data = yaml.safe_load(path.read_text())
        for body in data.values():
            raw = body.get("default_recipients") or []
            expected = [
                entry["email"] if isinstance(entry, dict) else entry for entry in raw
            ]
            assert cc_addresses(raw) == expected


def test_invalid_plain_address_names_the_address(tmp_path):
    _write(
        tmp_path,
        "qcs6490_hardware.yaml",
        {
            "qcs6490-rb3gen2": {
                "origin": "maestro",
                "default_recipients": ["Trilok Soni <not-an-email>"],
            }
        },
    )
    with pytest.raises(NotificationConfigError) as raised:
        load_subscriptions(tmp_path)
    error = raised.value
    assert error.file == "qcs6490_hardware.yaml"
    assert error.field == "qcs6490-rb3gen2.default_recipients.0.email"
    assert "invalid email address: Trilok Soni <not-an-email>" in str(error)


def test_invalid_issue_kind_names_file_and_field(tmp_path):
    _write(
        tmp_path,
        "tree.yaml",
        {
            "demo": {
                "url": "https://example.com/linux.git",
                "default_recipients": [
                    {
                        "email": "person@example.com",
                        "issues": ["flaky"],
                    }
                ],
            }
        },
    )
    with pytest.raises(NotificationConfigError) as raised:
        load_subscriptions(tmp_path)
    error = raised.value
    assert error.file == "tree.yaml"
    assert "issues" in error.field


def test_unknown_hardware_name_fails(tmp_path):
    _write(
        tmp_path,
        "qualcomm.yaml",
        {
            "qualcomm-weekly": {
                "recipients": ["tsoni@quicinc.com"],
                "hardware": ["missing-board"],
                "period_days": 7,
            }
        },
    )
    with pytest.raises(NotificationConfigError) as raised:
        load_metrics_rules(tmp_path, trees=set(), hardware={"qcs6490-rb3gen2"})
    assert raised.value.field == "qualcomm-weekly.hardware"
    assert "missing-board" in str(raised.value)


def test_overlapping_metrics_recipients_fail(tmp_path):
    _write(
        tmp_path,
        "a.yaml",
        {
            "weekly-a": {
                "recipients": ["tsoni@quicinc.com"],
                "hardware": ["qcs6490-rb3gen2"],
                "period_days": 7,
            }
        },
    )
    _write(
        tmp_path,
        "b.yaml",
        {
            "weekly-b": {
                "recipients": ["tsoni@quicinc.com"],
                "hardware": ["qcs6490-rb3gen2"],
                "origins": ["maestro"],
                "period_days": 7,
            }
        },
    )
    with pytest.raises(NotificationConfigError) as raised:
        load_metrics_rules(tmp_path, trees=set(), hardware={"qcs6490-rb3gen2"})
    assert "overlaps" in str(raised.value)
    assert raised.value.file == "b.yaml"

    separate = tmp_path / "separate"
    _write(
        separate,
        "boards.yaml",
        {
            "rb3": {
                "recipients": ["tsoni@quicinc.com"],
                "hardware": ["qcs6490-rb3gen2"],
                "origins": ["maestro"],
                "period_days": 7,
            },
            "ride": {
                "recipients": ["tsoni@quicinc.com"],
                "hardware": ["qcs9100-ride"],
                "origins": ["maestro"],
                "period_days": 7,
            },
        },
    )
    load_metrics_rules(
        separate,
        trees=set(),
        hardware={"qcs6490-rb3gen2", "qcs9100-ride"},
    )


def test_loader_keeps_mapping_email_on_the_cc_list(tmp_path):
    subscriptions = tmp_path / "notifications" / "subscriptions"
    _write(
        subscriptions,
        "demo.yaml",
        {
            "demo": {
                "url": "https://example.com/linux.git",
                "default_recipients": [
                    "plain@example.com",
                    {
                        "email": "opted@example.com",
                        "issues": ["boot", "test"],
                    },
                ],
                "reports": [{"main": None, "branch": "main"}],
            }
        },
    )
    _write(
        subscriptions,
        "board_hardware.yaml",
        {
            "board": {
                "origin": "maestro",
                "default_recipients": [
                    {
                        "email": "Owner <owner@example.com>",
                        "issues": ["boot"],
                    }
                ],
            }
        },
    )

    _, tree_props = process_submissions_files(
        base_dir=str(tmp_path),
        signup_folder="notifications/subscriptions",
    )
    recipients = next(iter(tree_props.values()))[0]["default_recipients"]
    assert recipients == ["plain@example.com", "opted@example.com"]

    _, hardware_props = process_hardware_submissions_files(
        base_dir=str(tmp_path),
        signup_folder="notifications/subscriptions",
    )
    assert hardware_props[("board", "maestro")]["default_recipients"] == [
        "Owner <owner@example.com>"
    ]
