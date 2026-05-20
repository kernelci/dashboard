from unittest.mock import patch

from kernelCI_app.queries.notifications import get_metrics_data

MODULE = "kernelCI_app.queries.notifications"

EMPTY_TOTALS = (0, 0, 0, 0, 0, 0)


class TestGetMetricsDataIntervals:
    @patch(f"{MODULE}.query_fetchall_work")
    @patch(f"{MODULE}.query_fetchone_work")
    def test_builds_current_and_previous_intervals_default_window(
        self, mock_fetchone, mock_fetchall
    ):
        mock_fetchone.return_value = EMPTY_TOTALS
        mock_fetchall.return_value = []

        get_metrics_data(start_days_ago=7, end_days_ago=0)

        fetchone_params = [
            mock_call.kwargs["params"] for mock_call in mock_fetchone.call_args_list
        ]
        fetchall_params = [
            mock_call.kwargs["params"] for mock_call in mock_fetchall.call_args_list
        ]

        curr = {"start_days_ago": "7 days", "end_days_ago": "0 days"}
        prev = {"start_days_ago": "14 days", "end_days_ago": "7 days"}

        assert curr in fetchone_params
        assert prev in fetchone_params
        assert curr in fetchall_params
        assert prev in fetchall_params

    @patch(f"{MODULE}.query_fetchall_work")
    @patch(f"{MODULE}.query_fetchone_work")
    def test_builds_custom_offset_window(self, mock_fetchone, mock_fetchall):
        mock_fetchone.return_value = EMPTY_TOTALS
        mock_fetchall.return_value = []

        get_metrics_data(start_days_ago=14, end_days_ago=7)

        fetchone_params = [
            mock_call.kwargs["params"] for mock_call in mock_fetchone.call_args_list
        ]
        fetchall_params = [
            mock_call.kwargs["params"] for mock_call in mock_fetchall.call_args_list
        ]

        curr = {"start_days_ago": "14 days", "end_days_ago": "7 days"}
        prev = {"start_days_ago": "21 days", "end_days_ago": "14 days"}

        assert curr in fetchone_params
        assert prev in fetchone_params
        assert curr in fetchall_params
        assert prev in fetchall_params
