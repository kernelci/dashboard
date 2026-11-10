import re
from urllib.parse import quote

from django.core.management.base import BaseCommand

import requests
from kernelCI_app.helpers.regzbot import record_regzbot_message
from kernelCI_app.models import Issues, RegzbotMessage


def kernelci_message_ids(index_html: str) -> list[str]:
    kernelci_id = re.compile(r'href="([^"]+@kernelci\.org)/"')

    def sent_at(message_id: str) -> int:
        head = message_id.split(".", 1)[0]
        return int(head) if head.isdigit() else 0

    return sorted(set(kernelci_id.findall(index_html)), key=sent_at)


def issue_id_from_regression(page_html: str) -> str | None:
    issue_id = re.compile(r"https://d\.kernelci\.org/i/([^\"<\s]+)")
    match = issue_id.search(page_html)
    return match.group(1) if match else None


def _fetch(url: str) -> str:
    response = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": "kernelci-dashboard-backfill"},
    )
    response.raise_for_status()
    return response.text


class Command(BaseCommand):
    help = (
        "Store regzbot Message-IDs for KernelCI issues on the lore index "
        "that are missing from regzbot_messages."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print the rows that would be inserted.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        lore_index = "https://linux-regtracking.leemhuis.info/regzbot/regression/lore/"
        message_ids = kernelci_message_ids(_fetch(lore_index))
        known_messages = set(
            RegzbotMessage.objects.values_list("message_id", flat=True)
        )
        known_issues = set(RegzbotMessage.objects.values_list("issue_id", flat=True))
        inserted = 0
        for message_id in message_ids:
            if message_id in known_messages:
                continue
            page_url = f"{lore_index}{quote(message_id, safe='@')}/"
            try:
                page = _fetch(page_url)
            except requests.RequestException as exc:
                self.stdout.write(f"skip {message_id}: {exc}")
                continue
            issue_id = issue_id_from_regression(page)
            if issue_id is None:
                self.stdout.write(f"skip {message_id}: no kernelci issue link")
                continue
            if issue_id in known_issues:
                self.stdout.write(f"skip {message_id}: {issue_id} already stored")
                continue
            if not Issues.objects.filter(pk=issue_id).exists():
                self.stdout.write(f"skip {message_id}: {issue_id} not in issues")
                continue
            if not dry_run:
                record_regzbot_message(issue_id=issue_id, message_id=message_id)
            known_issues.add(issue_id)
            known_messages.add(message_id)
            inserted += 1
            verb = "would store" if dry_run else "stored"
            self.stdout.write(f"{verb} {issue_id} {message_id}")
        verb = "would insert" if dry_run else "inserted"
        self.stdout.write(f"{verb} {inserted}")
