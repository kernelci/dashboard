from datetime import datetime, timedelta

from django.utils import timezone


def parse_interval(interval_str: str) -> datetime:
    """Turns an 'x days'/'x hours'/'x minutes' interval into an absolute
    timestamp relative to now (now - interval)."""
    parts = interval_str.split()
    if len(parts) != 2:
        raise ValueError(f"Invalid interval format: {interval_str}")

    value, unit = parts
    value = int(value)

    if unit.lower() in ["minute", "minutes"]:
        delta = timedelta(minutes=value)
    elif unit.lower() in ["hour", "hours"]:
        delta = timedelta(hours=value)
    elif unit.lower() in ["day", "days"]:
        delta = timedelta(days=value)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")

    return timezone.now() - delta
