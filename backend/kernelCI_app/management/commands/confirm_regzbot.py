from django.core.management.base import BaseCommand

from kernelCI_app.helpers.regzbot import confirm_pending_regzbot_messages


class Command(BaseCommand):
    help = (
        "HEAD regzbot tracking pages for stored Message-IDs. "
        "HTTP 200 stores the confirmation. 404, other statuses, and "
        "timeouts stay pending until the next run."
    )

    def handle(self, *args, **options):
        confirmed, pending = confirm_pending_regzbot_messages()
        self.stdout.write(
            f"Regzbot pages confirmed: {confirmed}; still pending: {pending}."
        )
