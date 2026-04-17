from datetime import datetime, timedelta
from datetime import timezone as dt_timezone
from typing import Optional, Tuple

from django.utils.timezone import now


def resolve_date_range(
    *,
    start_timestamp: Optional[str],
    end_timestamp: Optional[str],
) -> Tuple[datetime, datetime]:
    """Return (start_date, end_date) resolved from timestamps or interval.

    If both start_timestamp and end_timestamp are provided (as Unix second
    strings), they are converted to timezone-aware datetimes.

    end_date defaults to now(); start_date defaults to end_date - 7 days.
    start_date is computed relative to end_date (not now()) so that a
    past end_date without a start_date still produces a valid range.

    Raises ValueError if the timestamp strings are not valid numbers,
    or if start_date ends up after end_date.
    """
    end_date = (
        datetime.fromtimestamp(float(end_timestamp), tz=dt_timezone.utc)
        if end_timestamp is not None
        else now()
    )

    start_date = (
        datetime.fromtimestamp(float(start_timestamp), tz=dt_timezone.utc)
        if start_timestamp is not None
        else end_date - timedelta(days=7)
    )

    if start_date > end_date:
        raise ValueError("start_date must be before end_date")

    return start_date, end_date
