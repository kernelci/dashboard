import re
from unittest import TestCase
from unittest import mock
from unittest.mock import MagicMock, patch

from kernelCI_app.management.commands.notifications import (
    _fmt_change,
    compute_metrics_deltas,
    generate_metrics_report,
)
from kernelCI_app.tests.unitTests.commands.fixtures.metrics_notifications_data import (
    METRICS_NOTIFICATIONS_EXAMPLE_FILEPATH,
)
from kernelCI_app.typeModels.metrics_notifications import (
    BuildIncidentsCount,
    LabMetricsData,
    MetricsReportData,
    TopIssue,
)


def make_metrics_data(**overrides) -> MetricsReportData:
    """Generates a MetricsReportData object with the possibility to override any field."""
    defaults = dict(
        n_trees=105,
        n_checkouts=1000,
        n_builds=11000,
        n_tests=1000000,
        n_issues=10,
        n_incidents=75,
        build_incidents_by_origin={
            "maestro": BuildIncidentsCount(
                total_incidents=70,
                n_new_issues=1,
                n_total_issues=2,
                n_existing_issues=1,
            ),
            "redhat": BuildIncidentsCount(
                total_incidents=5, n_new_issues=0, n_total_issues=1, n_existing_issues=1
            ),
        },
        top_issues_by_origin={
            "maestro": {
                ("issue-1", 1): TopIssue(
                    id="issue-1",
                    version=1,
                    comment="First issue",
                    total_incidents=50,
                ),
                ("issue-2", 1): TopIssue(
                    id="issue-2",
                    version=1,
                    comment="Second issue",
                    total_incidents=20,
                ),
            },
            "redhat": {
                ("issue-3", 1): TopIssue(
                    id="issue-3",
                    version=1,
                    comment="Third issue",
                    total_incidents=5,
                ),
            },
        },
        lab_maps={
            "lava-collabora": LabMetricsData(
                builds=0, boots=50000, tests=450000, origin="maestro"
            ),
            "lava-broonie": LabMetricsData(
                builds=0, boots=25000, tests=475000, origin="maestro"
            ),
        },
        prev_n_trees=100,
        prev_n_checkouts=1000,
        prev_n_builds=10000,
        prev_n_tests=1500000,
        prev_lab_maps={
            "lava-collabora": LabMetricsData(
                builds=0, boots=50000, tests=700000, origin="maestro"
            ),
            "lava-broonie": LabMetricsData(
                builds=0, boots=100000, tests=650000, origin="maestro"
            ),
        },
    )
    defaults.update(overrides)
    return MetricsReportData(**defaults)


class TestFmtChange(TestCase):
    def test_no_change(self):
        assert _fmt_change(100, 100) == "0  (0%)"

    def test_positive_change_with_percentage(self):
        result = _fmt_change(110, 100)
        assert result == "+10  (+10%)"

    def test_negative_change_with_percentage(self):
        result = _fmt_change(90, 100)
        assert result == "-10  (-10%)"

    def test_large_numbers_comma_formatted(self):
        result = _fmt_change(10000, 11000)
        assert result == "-1,000  (-9%)"

    def test_show_percentage_false(self):
        result = _fmt_change(105, 100, show_percentage=False)
        assert "%" not in result
        assert result == "+5"

    def test_prev_zero_with_percentage(self):
        # Cannot compute a percentage when prev is 0
        result = _fmt_change(10, 0, show_percentage=True)
        assert result == "+10"


class TestComputeMetricsDeltas(TestCase):
    def test_returns_all_expected_keys(self):
        data = make_metrics_data()
        deltas = compute_metrics_deltas(data)
        expected = {
            "n_trees": "+5",
            "n_checkouts": "0  (0%)",
            "n_builds": "+1,000  (+10%)",
            "n_tests": "-500,000  (-33%)",
            "labs": {
                "lava-collabora": "-250,000  (-36%)",
                "lava-broonie": "-175,000  (-27%)",
            },
            "new_lab_keys": set(),
            "extinct_lab_keys": set(),
            "n_total_lab_activity": "-425,000  (-31%)",
        }

        for key, value in deltas.items():
            assert key in expected
            assert value == expected[key]

    def test_new_lab_detected(self):
        data = make_metrics_data(
            lab_maps={
                "lava-collabora": LabMetricsData(
                    builds=0, boots=100, tests=500, origin="maestro"
                ),
                "new-lab": LabMetricsData(
                    builds=0, boots=50, tests=200, origin="maestro"
                ),
            },
            prev_lab_maps={
                "lava-collabora": LabMetricsData(
                    builds=0, boots=100, tests=500, origin="maestro"
                ),
            },
        )
        deltas = compute_metrics_deltas(data)
        assert "new-lab" in deltas["new_lab_keys"]
        assert "lava-collabora" not in deltas["new_lab_keys"]
        assert deltas["labs"]["new-lab"] == "+200"  # prev=0, no percentage

    def test_extinct_lab_detected(self):
        data = make_metrics_data(
            lab_maps={
                "lava-collabora": LabMetricsData(
                    builds=0, boots=100, tests=500, origin="maestro"
                ),
            },
            prev_lab_maps={
                "lava-collabora": LabMetricsData(
                    builds=0, boots=100, tests=500, origin="maestro"
                ),
                "old-lab": LabMetricsData(
                    builds=0, boots=200, tests=1000, origin="maestro"
                ),
            },
        )
        deltas = compute_metrics_deltas(data)
        assert "old-lab" in deltas["extinct_lab_keys"]
        assert "lava-collabora" not in deltas["extinct_lab_keys"]
        assert "(-100%)" in deltas["labs"]["old-lab"]

    def test_lab_missing_in_prev_period(self):
        data = make_metrics_data(
            lab_maps={
                "new-lab": LabMetricsData(
                    builds=0, boots=100, tests=500, origin="maestro"
                ),
            },
            prev_lab_maps={},
        )
        deltas = compute_metrics_deltas(data)
        # prev is 0, so no percentage
        assert deltas["labs"]["new-lab"] == "+500"
        assert "new-lab" in deltas["new_lab_keys"]


MOCK_MODULE = "kernelCI_app.management.commands.notifications"


class TestGenerateMetricsReport(TestCase):
    @patch(f"{MOCK_MODULE}.send_email_report")
    @patch(f"{MOCK_MODULE}.get_metrics_data")
    @patch(f"{MOCK_MODULE}.get_running_instance", return_value="staging")
    def test_does_not_run_on_staging(self, mock_instance, mock_get, mock_send):
        generate_metrics_report(email_service=MagicMock(), email_args=MagicMock())
        mock_get.assert_not_called()
        mock_send.assert_not_called()
        mock_instance.assert_called_once()

    @patch(f"{MOCK_MODULE}.send_email_report")
    @patch(f"{MOCK_MODULE}.setup_jinja_template")
    @patch(f"{MOCK_MODULE}.get_metrics_data")
    @patch(f"{MOCK_MODULE}.get_running_instance", return_value="production")
    def test_default_success(self, mock_instance, mock_get, mock_template, mock_send):
        mock_get.return_value = make_metrics_data()
        mock_template.return_value.render.return_value = "rendered content"
        generate_metrics_report(email_service=MagicMock(), email_args=MagicMock())
        mock_get.assert_called_once_with(start_days_ago=7, end_days_ago=0)
        mock_template.assert_called_once_with("metrics_report.txt.j2")
        mock_instance.assert_called_once()
        mock_send.assert_called_once()

    @patch(f"{MOCK_MODULE}.send_email_report")
    @patch(f"{MOCK_MODULE}.setup_jinja_template")
    @patch(f"{MOCK_MODULE}.get_metrics_data")
    @patch(f"{MOCK_MODULE}.get_running_instance", return_value="production")
    def test_render_receives_fields(
        self, mock_instance, mock_get, mock_template, mock_send
    ):
        mock_get.return_value = make_metrics_data()
        mock_template.return_value.render.return_value = "rendered content"

        generate_metrics_report(email_service=MagicMock(), email_args=MagicMock())

        mock_instance.assert_called_once()
        mock_send.assert_called_once()
        mock_template.return_value.render.assert_called_once_with(
            n_trees=105,
            n_checkouts=1000,
            n_builds=11000,
            n_tests=1000000,
            n_issues=10,
            n_incidents=75,
            build_incidents_by_origin=mock.ANY,
            top_issues_by_origin=mock.ANY,
            lab_maps=mock.ANY,
            prev_n_trees=100,
            prev_n_checkouts=1000,
            prev_n_builds=10000,
            prev_n_tests=1500000,
            prev_lab_maps=mock.ANY,
            start_datetime=mock.ANY,
            end_datetime=mock.ANY,
            deltas=mock.ANY,
            lab_spacing=mock.ANY,
        )

    @patch(f"{MOCK_MODULE}.send_email_report")
    @patch(f"{MOCK_MODULE}.setup_jinja_template")
    @patch(f"{MOCK_MODULE}.get_metrics_data")
    @patch(f"{MOCK_MODULE}.get_running_instance", return_value="production")
    def test_report_content_is_rendered_output(
        self, mock_instance, mock_get, mock_template, mock_send
    ):
        mock_get.return_value = make_metrics_data()
        mock_template.return_value.render.return_value = "rendered content"
        generate_metrics_report(email_service=MagicMock(), email_args=MagicMock())
        report_arg = mock_send.call_args.kwargs["report"]
        assert report_arg["content"] == "rendered content"
        mock_instance.assert_called_once()


class TestMetricsReportTemplate(TestCase):
    """Integration tests for the contents of the jinja template."""

    @staticmethod
    def render_report(**overrides) -> str:
        """Render the real template with the given data overrides, return the content string."""
        data = make_metrics_data(**overrides)
        captured = {}

        with (
            patch(
                f"{MOCK_MODULE}.send_email_report",
                side_effect=lambda *, service, report, **kwargs: captured.update(
                    report
                ),
            ),
            patch(f"{MOCK_MODULE}.get_metrics_data", return_value=data),
            patch(f"{MOCK_MODULE}.get_running_instance", return_value="production"),
        ):
            generate_metrics_report(email_service=MagicMock(), email_args=MagicMock())

        content = captured["content"]

        # Remove the "Period: ..." line since it changes every second and is not relevant to the tests.
        content = re.sub(r"^Period:.*\n", "", content, flags=re.MULTILINE)

        return content

    def test_full_report_structure(self):
        content = self.render_report()

        # Comparing the full output with a known report will test the whole structure.
        # If the template changes, we can rerun the render with the base_data (change it manually)
        # and update the known report.
        with open(METRICS_NOTIFICATIONS_EXAMPLE_FILEPATH) as f:
            expected = f.read()

        assert content == expected

    def test_no_build_regressions_message_shown(self):
        content = self.render_report(build_incidents_by_origin={})
        assert "No build regressions to show in this period." in content

    def test_lab_count_unchanged(self):
        lab = LabMetricsData(builds=0, boots=100, tests=500, origin="maestro")
        content = self.render_report(
            lab_maps={"lava-collabora": lab},
            prev_lab_maps={"lava-collabora": lab},
        )
        assert "unchanged from last week" in content

    def test_lab_count_increased(self):
        lab = LabMetricsData(builds=0, boots=100, tests=500, origin="maestro")
        content = self.render_report(
            lab_maps={"lava-collabora": lab, "lava-broonie": lab},
            prev_lab_maps={"lava-collabora": lab},
        )
        assert "1 more than last week" in content

    def test_lab_count_decreased(self):
        lab = LabMetricsData(builds=0, boots=100, tests=500, origin="maestro")
        content = self.render_report(
            lab_maps={"lava-collabora": lab},
            prev_lab_maps={"lava-collabora": lab, "lava-broonie": lab},
        )
        assert "1 fewer than last week" in content

    def test_new_lab_marked_with_asterisk(self):
        lab = LabMetricsData(builds=0, boots=100, tests=500, origin="maestro")
        content = self.render_report(
            lab_maps={
                "lava-collabora": lab,
                "brand-new-lab": lab,
            },
            prev_lab_maps={"lava-collabora": lab},
        )
        assert re.search(r"^.*brand-new-lab \*.*$", content, re.MULTILINE)
        assert not re.search(r"^.*lava-collabora \*.*$", content, re.MULTILINE)

    def test_extinct_lab(self):
        lab = LabMetricsData(builds=0, boots=100, tests=500, origin="maestro")
        content = self.render_report(
            lab_maps={"lava-collabora": lab},
            prev_lab_maps={"lava-collabora": lab, "gone-lab": lab},
        )
        assert re.search(
            r"^.*gone-lab.*0.*0.*0.*-500.*\(-100%\).*$",
            content,
            re.MULTILINE,
        )
