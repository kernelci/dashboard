from datetime import datetime, timezone
from unittest.mock import patch

from kernelCI_app.queries.notifications import get_metrics_data, interval_params

MODULE = "kernelCI_app.queries.notifications"

EMPTY_TOTALS = (0, 0, 0, 0, 0, 0)
FIXED_NOW = datetime(2026, 6, 20, 12, 0, tzinfo=timezone.utc)


class TestGetMetricsDataIntervals:
    @patch(f"{MODULE}.query_fetchall_work")
    @patch(f"{MODULE}.query_fetchone_work")
    @patch(f"{MODULE}.datetime")
    def test_builds_current_and_previous_intervals_default_window(
        self, mock_datetime, mock_fetchone, mock_fetchall
    ):
        mock_datetime.now.return_value = FIXED_NOW
        mock_datetime.combine.side_effect = datetime.combine
        mock_fetchone.return_value = EMPTY_TOTALS
        mock_fetchall.return_value = []

        get_metrics_data(start_days_ago=7, end_days_ago=0)

        fetchone_params = [
            mock_call.kwargs["params"] for mock_call in mock_fetchone.call_args_list
        ]
        fetchall_params = [
            mock_call.kwargs["params"] for mock_call in mock_fetchall.call_args_list
        ]

        curr = interval_params(7, 0)
        prev = interval_params(14, 7)

        assert curr in fetchone_params
        assert prev in fetchone_params
        assert curr in fetchall_params
        assert prev in fetchall_params

    @patch(f"{MODULE}.query_fetchall_work")
    @patch(f"{MODULE}.query_fetchone_work")
    @patch(f"{MODULE}.datetime")
    def test_builds_custom_offset_window(
        self, mock_datetime, mock_fetchone, mock_fetchall
    ):
        mock_datetime.now.return_value = FIXED_NOW
        mock_datetime.combine.side_effect = datetime.combine
        mock_fetchone.return_value = EMPTY_TOTALS
        mock_fetchall.return_value = []

        get_metrics_data(start_days_ago=14, end_days_ago=7)

        fetchone_params = [
            mock_call.kwargs["params"] for mock_call in mock_fetchone.call_args_list
        ]
        fetchall_params = [
            mock_call.kwargs["params"] for mock_call in mock_fetchall.call_args_list
        ]

        curr = interval_params(14, 7)
        prev = interval_params(21, 14)

        assert curr in fetchone_params
        assert prev in fetchone_params
        assert curr in fetchall_params
        assert prev in fetchall_params


class TestIntervalParams:
    @patch(f"{MODULE}.datetime")
    def test_builds_half_open_interval(self, mock_datetime):
        mock_datetime.now.return_value = datetime(
            2026, 6, 18, 12, 0, tzinfo=timezone.utc
        )
        mock_datetime.combine.side_effect = datetime.combine

        params = interval_params(12, 4)

        assert params["start_date"] == "2026-06-06T00:00:00+00:00"
        assert params["end_date"] == "2026-06-14T00:00:00+00:00"
