import ast
import json
from datetime import timedelta

from django.utils import timezone

from kernelCI_app.helpers.logger import log_message
from kernelCI_app.management.commands.helpers.summary import ReportConfigs, TreeKey
from kernelCI_cache.models import NotificationsCheckout, NotificationsIssue
from kernelCI_cache.typeModels.databases import PossibleIssueType
from kernelCI_cache.utils import get_current_timestamp_kcidb_format

RESEND_INTERVAL_HOURS = 12


def _canonical_path(path: list[str] | str | None) -> str:
    """Normalize configured filters and the JSON or Python list strings in older rows."""
    if isinstance(path, str) and path.lstrip().startswith("["):
        try:
            filters = json.loads(path)
        except json.JSONDecodeError:
            try:
                filters = ast.literal_eval(path.strip())
            except (ValueError, SyntaxError):
                return path
        if isinstance(filters, list) and all(isinstance(item, str) for item in filters):
            path = filters
    if isinstance(path, list):
        return json.dumps(path) if path else "%"
    return path or "%"


def mark_checkout_notification_as_sent(
    *,
    msg_id: str,
    checkout_id: str,
    git_repository_branch: str,
    git_repository_url: str,
    origin: str,
    path: list[str] | str | None,
) -> bool:
    try:
        timestamp = get_current_timestamp_kcidb_format()
        NotificationsCheckout.objects.using("notifications").create(
            notification_message_id=msg_id,
            notification_sent=timestamp,
            checkout_id=checkout_id,
            git_repository_branch=git_repository_branch,
            git_repository_url=git_repository_url,
            origin=origin,
            path=_canonical_path(path),
        )
        return True
    except Exception as e:
        print(f"Error storing notification checkout: {e}")
        return False


def mark_issue_notification_sent(
    *,
    msg_id: str,
    issue_id: str,
    issue_version: int,
    issue_type: PossibleIssueType,
) -> bool:
    """Creates an entry for an issue notification"""
    try:
        timestamp = get_current_timestamp_kcidb_format()
        NotificationsIssue.objects.using("notifications").update_or_create(
            issue_id=issue_id,
            issue_version=issue_version,
            issue_type=issue_type,
            defaults={
                "notification_message_id": msg_id,
                "notification_sent": timestamp,
            },
        )
        return True
    except Exception as e:
        log_message(f"Error marking issue notification sent:\n{e}")
        return False


def mark_issue_notification_not_sent(
    *,
    issue_id: str,
    issue_version: int,
    issue_type: PossibleIssueType,
) -> bool:
    """Creates an entry for an issue without notifications

    Returns:
      True if an issue already exists in the database, or was created.

      False if any exception occurs
    """
    try:
        issue_exists = (
            NotificationsIssue.objects.using("notifications")
            .filter(
                issue_id=issue_id,
                issue_version=issue_version,
            )
            .exists()
        )

        if not issue_exists:
            NotificationsIssue.objects.using("notifications").create(
                issue_id=issue_id,
                issue_version=issue_version,
                issue_type=issue_type,
            )
        return True
    except Exception as e:
        log_message(f"Error marking issue notification not sent:\n{e}")
        return False


def get_unsent_checkout_reports(
    tree_prop_map: dict[TreeKey, ReportConfigs],
) -> dict[TreeKey, ReportConfigs]:
    """Keep reports whose tree and path have no delivery within the resend interval."""
    if not tree_prop_map:
        return {}

    since = timezone.now() - timedelta(hours=RESEND_INTERVAL_HOURS)
    recent_deliveries = (
        NotificationsCheckout.objects.using("notifications")
        .filter(notification_sent__gte=since)
        .values_list("git_repository_branch", "git_repository_url", "origin", "path")
    )
    sent = {
        (branch, url, origin, _canonical_path(path))
        for branch, url, origin, path in recent_deliveries
    }
    pending = {}
    for tree, reports in tree_prop_map.items():
        remaining = [
            report
            for report in reports
            if (*tree, _canonical_path(report.get("path"))) not in sent
        ]
        if remaining:
            pending[tree] = remaining

    return pending
