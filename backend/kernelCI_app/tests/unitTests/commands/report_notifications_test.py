from unittest import TestCase

from kernelCI_app.management.commands.helpers.common import setup_jinja_template
from kernelCI_app.management.commands.notifications import (
    generate_boot_issue_report,
    generate_build_issue_report,
)
from kernelCI_app.tests.unitTests.commands.fixtures.report_notifications_data import (
    ISSUE_BOOT_REPORT_EXAMPLE_FILEPATH,
    ISSUE_BUILD_REPORT_EXAMPLE_FILEPATH,
    MESSAGE_ID,
    TEST_REPORT_EXAMPLE_FILEPATH,
    make_boot_issue,
    make_build_issue,
    make_test,
)

LORE_LINK = f"Link: https://lore.kernel.org/all/{MESSAGE_ID.strip('<>')}/"


class TestReportTemplates(TestCase):
    """Golden-file tests for the regression report templates.

    Render the real templates with fixed data and compare against committed
    example files. When a template changes, regenerate the fixtures with
    `./manage.py refresh_report_examples` and review the diff.
    """

    @staticmethod
    def render_build_report(*, with_range: bool = True) -> str:
        issue, incidents = make_build_issue(with_range=with_range)
        return generate_build_issue_report(issue, incidents, MESSAGE_ID)["content"]

    @staticmethod
    def render_boot_report(*, with_range: bool = True) -> str:
        issue, incidents = make_boot_issue(with_range=with_range)
        return generate_boot_issue_report(issue, incidents, MESSAGE_ID)["content"]

    @staticmethod
    def render_test_report(*, with_range: bool = True) -> str:
        test = make_test(with_range=with_range)
        return setup_jinja_template("test_report.txt.j2").render(
            test=test, message_id=MESSAGE_ID.strip("<>")
        )

    def test_build_report_structure(self):
        with open(ISSUE_BUILD_REPORT_EXAMPLE_FILEPATH) as f:
            assert self.render_build_report() == f.read()

    def test_boot_report_structure(self):
        with open(ISSUE_BOOT_REPORT_EXAMPLE_FILEPATH) as f:
            assert self.render_boot_report() == f.read()

    def test_test_report_structure(self):
        with open(TEST_REPORT_EXAMPLE_FILEPATH) as f:
            assert self.render_test_report() == f.read()

    def test_reports_have_attribution_and_lore_link(self):
        for render in (
            self.render_build_report,
            self.render_boot_report,
            self.render_test_report,
        ):
            content = render()
            assert "Reported-by: kernelci.org bot <bot@kernelci.org>" in content
            assert LORE_LINK in content

    def test_reports_have_regzbot_range_at_the_end(self):
        for render in (
            self.render_build_report,
            self.render_boot_report,
            self.render_test_report,
        ):
            content = render()
            assert "#regzbot introduced: a1b2c3d4" in content
            assert "..ddd664bb" in content
            # The regzbot commands are bot-only, so they sit at the end of the
            # report, after all the human-facing content.
            assert content.index("#regzbot introduced:") > content.index("dashboard")
            # The title command is omitted on purpose: regzbot falls back to
            # the mail subject, which carries more information.
            assert "#regzbot title:" not in content

    def test_reports_omit_regzbot_block_without_range(self):
        # No last passing commit -> no range -> the whole regzbot block is
        # omitted, since regzbot won't act without an "introduced:" command.
        for render in (
            self.render_build_report,
            self.render_boot_report,
            self.render_test_report,
        ):
            content = render(with_range=False)
            assert "#regzbot" not in content
            assert "Reported-by: kernelci.org bot <bot@kernelci.org>" in content
            assert "#kernelci" in content
