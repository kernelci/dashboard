from django.test import SimpleTestCase, override_settings
from unittest.mock import Mock, patch

from kernelCI_app.management.commands.helpers.healthcheck import (
    _resolve_monitoring_url,
    run_with_healthcheck_monitoring,
)

TEST_BASE_URL = "https://example.com"


@override_settings(
    HEALTHCHECK_MONITORING_PATH_MAP={
        "job-1": "private-token",
        "job-2": "something/with/slashes",
    },
    HEALTHCHECK_BASE_URL=TEST_BASE_URL,
)
class TestRunWithHealthcheckMonitoring(SimpleTestCase):
    def test_resolve_monitoring_url_success(self):
        result = _resolve_monitoring_url(monitoring_id="job-1", status="start")
        self.assertEqual(result, f"{TEST_BASE_URL}/private-token/start")

    def test_resolve_monitoring_url_success_status_no_suffix(self):
        result = _resolve_monitoring_url(monitoring_id="job-1", status="success")
        self.assertEqual(result, f"{TEST_BASE_URL}/private-token")

    @patch("kernelCI_app.management.commands.helpers.healthcheck.requests.get")
    def test_success_path_pings_start_and_success(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        result = run_with_healthcheck_monitoring(
            monitoring_id="job-1", action=lambda: "ok"
        )

        assert result == "ok"
        assert mock_get.call_count == 2
        mock_get.assert_any_call(f"{TEST_BASE_URL}/private-token/start", timeout=10)
        mock_get.assert_any_call(f"{TEST_BASE_URL}/private-token", timeout=10)

    @patch("kernelCI_app.management.commands.helpers.healthcheck.requests.get")
    def test_failure_path_pings_start_and_fail(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        with self.assertRaisesRegex(RuntimeError, "boom"):
            run_with_healthcheck_monitoring(
                monitoring_id="job-1",
                action=lambda: (_ for _ in ()).throw(RuntimeError("boom")),
            )

        assert mock_get.call_count == 2
        mock_get.assert_any_call(f"{TEST_BASE_URL}/private-token/start", timeout=10)
        mock_get.assert_any_call(f"{TEST_BASE_URL}/private-token/fail", timeout=10)

    @patch("kernelCI_app.management.commands.helpers.healthcheck.requests.get")
    def test_no_monitoring_id_skips_pings(self, mock_get):
        result = run_with_healthcheck_monitoring(monitoring_id=None, action=lambda: 42)

        assert result == 42
        mock_get.assert_not_called()

    @patch("kernelCI_app.management.commands.helpers.healthcheck.requests.get")
    def test_unknown_monitoring_id_skips_network_and_runs_action(self, mock_get):
        result = run_with_healthcheck_monitoring(
            monitoring_id="missing-id", action=lambda: "ran"
        )

        assert result == "ran"
        mock_get.assert_not_called()
