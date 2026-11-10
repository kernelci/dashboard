from django.test import SimpleTestCase

from kernelCI_app.management.commands.backfill_regzbot_messages import (
    issue_id_from_regression,
    kernelci_message_ids,
)


class TestBackfillRegzbotParsers(SimpleTestCase):
    def test_parses_kernelci_entries_oldest_first(self):
        index = (
            '<a href="20.1.9@kernelci.org/">a</a>'
            '<a href="10.2.8@kernelci.org/">b</a>'
            '<a href="abc@gmail.com/">c</a>'
        )
        self.assertEqual(
            kernelci_message_ids(index),
            ["10.2.8@kernelci.org", "20.1.9@kernelci.org"],
        )
        self.assertEqual(
            issue_id_from_regression('<a href="https://d.kernelci.org/i/maestro:abc">'),
            "maestro:abc",
        )
        self.assertIsNone(issue_id_from_regression("<p>no link</p>"))
