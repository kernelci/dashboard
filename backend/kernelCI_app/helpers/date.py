from kernelCI_app.helpers.errorHandling import ExceptionWithJsonResponse
from datetime import datetime, timezone
from typing import Tuple


def parseIntervalInDaysGetParameter(intervalInDays: str) -> int:
    try:
        parsedIntervalInDays = int(intervalInDays)
        if parsedIntervalInDays < 1:
            raise ExceptionWithJsonResponse(
                "Invalid intervalInDays, must be bigger than 0", 400
            )
        return parsedIntervalInDays
    except ValueError:
        raise ExceptionWithJsonResponse("Invalid intervalInDays, must be a number", 400)


def parse_start_and_end_timestamps_in_seconds_to_datetime(
    start_timestamp_in_seconds: str, end_timestamp_in_seconds: str
) -> Tuple[datetime, datetime]:
    try:
        start_timestamp = datetime.fromtimestamp(int(start_timestamp_in_seconds), timezone.utc)
        end_timestamp = datetime.fromtimestamp(int(end_timestamp_in_seconds), timezone.utc)
        if start_timestamp >= end_timestamp:
            raise ExceptionWithJsonResponse(
                ("Invalid start_timestamp_in_seconds and end_timestamp_in_seconds, "
                 "start_timestamp_in_seconds must be smaller than end_timestamp_in_seconds"),
                400,
            )
        return start_timestamp, end_timestamp
    except ValueError:
        raise ExceptionWithJsonResponse(
            "Invalid start_timestamp_in_seconds or end_timestamp_in_seconds, must be a number", 400
        )
