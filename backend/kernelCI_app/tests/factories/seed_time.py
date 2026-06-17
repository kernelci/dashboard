from datetime import datetime, time, timedelta, timezone

from django.utils import timezone as django_timezone

# Seeded rows land at UTC midnight on days_ago 0..SEED_DAY_SPAN-1 so that both the
# default (7, 0) current window and the (14, 7) previous window contain data.
SEED_DAY_SPAN = 22


def seeded_timestamp(*, days_ago: int = 1) -> datetime:
    """UTC midnight for seeded data, sitting exactly on interval_params day boundaries."""
    day = django_timezone.now().date() - timedelta(days=days_ago)
    return datetime.combine(day, time.min, tzinfo=timezone.utc)


def seeded_timestamp_for_index(n: int) -> datetime:
    """Cycle a factory Sequence index across SEED_DAY_SPAN consecutive midnights."""
    return seeded_timestamp(days_ago=n % SEED_DAY_SPAN)
