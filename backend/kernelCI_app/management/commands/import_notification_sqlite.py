import os
import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from kernelCI_cache.models import NotificationsCheckout, NotificationsIssue


def new_rows(rows, key, existing):
    seen = set(existing)
    chosen = []
    for row in rows:
        row_key = key(row)
        if row_key in seen:
            continue
        seen.add(row_key)
        chosen.append(row)
    return chosen


class Command(BaseCommand):
    help = (
        "Copy notification history from notifications.sqlite3 into PostgreSQL. "
        "Running it again does not insert rows that are already there."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default=None,
            help=(
                "Path to notifications.sqlite3. "
                "Defaults to BACKEND_VOLUME_DIR/notifications.sqlite3."
            ),
        )

    def handle(self, *args, **options):
        path = options["path"] or (
            Path(settings.BACKEND_VOLUME_DIR) / "notifications.sqlite3"
        )
        if not os.path.exists(path):
            self.stdout.write(f"No notification sqlite file at {path}; skipping.")
            return

        uri = f"{Path(path).resolve().as_uri()}?mode=ro"
        with sqlite3.connect(uri, uri=True) as conn:
            conn.row_factory = sqlite3.Row
            checkouts = [
                dict(row)
                for row in conn.execute(
                    """
                    SELECT notification_message_id, notification_sent, checkout_id,
                           git_repository_branch, git_repository_url, origin, path
                    FROM notifications_checkout
                    """
                )
            ]
            issues = [
                dict(row)
                for row in conn.execute(
                    """
                    SELECT notification_message_id, notification_sent, issue_id,
                           issue_version, issue_type
                    FROM notifications_issue
                    """
                )
            ]

        new_checkouts = new_rows(
            checkouts,
            lambda row: row["notification_message_id"],
            NotificationsCheckout.objects.values_list(
                "notification_message_id", flat=True
            ),
        )
        new_issues = new_rows(
            issues,
            lambda row: (row["issue_id"], row["issue_version"]),
            NotificationsIssue.objects.values_list("issue_id", "issue_version"),
        )

        with transaction.atomic():
            NotificationsCheckout.objects.bulk_create(
                [NotificationsCheckout(**row) for row in new_checkouts]
            )
            NotificationsIssue.objects.bulk_create(
                [NotificationsIssue(**row) for row in new_issues]
            )

        self.stdout.write(
            f"Imported {len(new_checkouts)} checkout rows and "
            f"{len(new_issues)} issue rows "
            f"({len(checkouts) - len(new_checkouts)} checkout and "
            f"{len(issues) - len(new_issues)} issue rows already present)."
        )
