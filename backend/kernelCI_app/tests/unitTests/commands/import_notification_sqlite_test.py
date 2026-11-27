from kernelCI_app.management.commands.import_notification_sqlite import new_rows


def test_new_rows_keeps_one_row_per_new_key():
    checkouts = [
        {"notification_message_id": "<a>"},
        {"notification_message_id": "<a>"},
        {"notification_message_id": "<b>"},
    ]
    kept = new_rows(checkouts, lambda row: row["notification_message_id"], {"<b>"})
    assert [row["notification_message_id"] for row in kept] == ["<a>"]

    issues = [
        {"issue_id": "i", "issue_version": 1},
        {"issue_id": "i", "issue_version": 1},
        {"issue_id": "j", "issue_version": 2},
    ]
    kept = new_rows(
        issues,
        lambda row: (row["issue_id"], row["issue_version"]),
        {("j", 2)},
    )
    assert [(row["issue_id"], row["issue_version"]) for row in kept] == [("i", 1)]
