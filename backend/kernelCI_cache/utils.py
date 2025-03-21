from datetime import datetime, timezone, timedelta


def get_timestamp_kcidb_format(timestamp: datetime) -> str:
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
    timestamp_str = timestamp_str[:-3] + " " + timestamp.strftime("%z")
    return timestamp_str


def get_current_timestamp_kcidb_format() -> str:
    tz_offset = timezone(timedelta(hours=-3))
    timestamp = datetime.now(tz_offset)
    return get_timestamp_kcidb_format(timestamp)
