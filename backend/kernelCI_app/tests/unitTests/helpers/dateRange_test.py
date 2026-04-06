from datetime import datetime, timedelta, timezone as dt_timezone
from unittest.mock import patch

import pytest

from kernelCI_app.helpers.dateRange import resolve_date_range

FIXED_NOW = datetime(2026, 4, 6, 12, 0, 0, tzinfo=dt_timezone.utc)

# Arbitrary round-number timestamps ~5 days apart, no domain significance.
# Chosen for readability; any two valid timestamps where start < end would work.
#   2023-11-14 22:13:20 UTC
NOV_14_2023_TS = "1700000000"
NOV_14_2023 = datetime(2023, 11, 14, 22, 13, 20, tzinfo=dt_timezone.utc)

#   2023-11-19 22:13:20 UTC  (5 days later)
NOV_19_2023_TS = "1700432000"
NOV_19_2023 = datetime(2023, 11, 19, 22, 13, 20, tzinfo=dt_timezone.utc)


class TestResolveDateRange:
    """Unit tests for resolve_date_range."""

    @patch("kernelCI_app.helpers.dateRange.now", return_value=FIXED_NOW)
    def test_defaults_when_no_timestamps(self, _mock_now):
        """Both None → end=now, start=now-7d."""
        start, end = resolve_date_range(start_timestamp=None, end_timestamp=None)

        assert end == FIXED_NOW
        assert start == FIXED_NOW - timedelta(days=7)

    def test_both_timestamps_provided(self):
        """Explicit start and end are converted to UTC datetimes."""
        start, end = resolve_date_range(
            start_timestamp=NOV_14_2023_TS, end_timestamp=NOV_19_2023_TS
        )

        assert start == NOV_14_2023
        assert end == NOV_19_2023

    @patch("kernelCI_app.helpers.dateRange.now", return_value=FIXED_NOW)
    def test_only_start_provided(self, _mock_now):
        """Only start → end defaults to now()."""
        start, end = resolve_date_range(
            start_timestamp=NOV_14_2023_TS, end_timestamp=None
        )

        assert start == NOV_14_2023
        assert end == FIXED_NOW

    @patch("kernelCI_app.helpers.dateRange.now", return_value=FIXED_NOW)
    def test_only_end_provided(self, _mock_now):
        """Only end → start defaults to now()-7d."""
        # end_ts must be >= FIXED_NOW - 7d, so we use FIXED_NOW itself
        fixed_now_ts = str(int(FIXED_NOW.timestamp()))

        start, end = resolve_date_range(
            start_timestamp=None, end_timestamp=fixed_now_ts
        )

        assert start == FIXED_NOW - timedelta(days=7)
        assert end == datetime.fromtimestamp(
            int(FIXED_NOW.timestamp()), tz=dt_timezone.utc
        )

    def test_start_after_end_raises(self):
        """start > end → ValueError (Nov 19 as start, Nov 14 as end)."""
        with pytest.raises(ValueError, match="start_date must be before end_date"):
            resolve_date_range(
                start_timestamp=NOV_19_2023_TS, end_timestamp=NOV_14_2023_TS
            )

    def test_float_timestamps(self):
        """Fractional seconds are accepted (Nov 14 + 0.5s, Nov 19 + 0.9s)."""
        start, end = resolve_date_range(
            start_timestamp=f"{NOV_14_2023_TS}.5",
            end_timestamp=f"{NOV_19_2023_TS}.9",
        )

        assert start == datetime.fromtimestamp(1700000000.5, tz=dt_timezone.utc)
        assert end == datetime.fromtimestamp(1700432000.9, tz=dt_timezone.utc)

    def test_invalid_start_raises(self):
        """Non-numeric start → ValueError."""
        with pytest.raises(ValueError):
            resolve_date_range(
                start_timestamp="not-a-number", end_timestamp=NOV_19_2023_TS
            )

    def test_invalid_end_raises(self):
        """Non-numeric end → ValueError."""
        with pytest.raises(ValueError):
            resolve_date_range(start_timestamp=NOV_14_2023_TS, end_timestamp="abc")

    def test_equal_timestamps(self):
        """start == end is valid (zero-width range)."""
        start, end = resolve_date_range(
            start_timestamp=NOV_14_2023_TS, end_timestamp=NOV_14_2023_TS
        )

        assert start == end

    def test_returned_datetimes_are_utc(self):
        """Both returned datetimes carry UTC timezone info."""
        start, end = resolve_date_range(
            start_timestamp=NOV_14_2023_TS, end_timestamp=NOV_19_2023_TS
        )

        assert start.tzinfo == dt_timezone.utc
        assert end.tzinfo == dt_timezone.utc
