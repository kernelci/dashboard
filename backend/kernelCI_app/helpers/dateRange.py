from datetime import datetime, timedelta, timezone as dt_timezone
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

    Otherwise, end_date is set to now() and start_date to
    now() - 7 days.

    Raises ValueError if the timestamp strings are not valid numbers.
    """
    if start_timestamp is not None and end_timestamp is not None:
        start_date = datetime.fromtimestamp(float(start_timestamp), tz=dt_timezone.utc)
        end_date = datetime.fromtimestamp(float(end_timestamp), tz=dt_timezone.utc)
        return start_date, end_date

    end_date = now()
    start_date = end_date - timedelta(days=7)
    return start_date, end_date
