from django.utils import timezone
from datetime import timedelta

DEFAULT_QUERY_TIME_INTERVAL = {'days': 7}


def getQueryTimeInterval(**kwargs):
    if not kwargs:
        return timezone.now() - timedelta(**DEFAULT_QUERY_TIME_INTERVAL)
    return timezone.now() - timedelta(**kwargs)
