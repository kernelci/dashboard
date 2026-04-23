from typing import Optional


def get_build_duration_clause(
    builds_duration: tuple[Optional[int], Optional[int]],
) -> str:
    clause = ""
    duration_min, duration_max = builds_duration
    if duration_min is not None:
        clause += "AND builds.duration >= %(build_duration_min)s\n"
    if duration_max is not None:
        clause += "AND builds.duration <= %(build_duration_max)s\n"
    return clause


def get_boot_test_duration_clause(
    boots_duration: tuple[Optional[int], Optional[int]],
    tests_duration: tuple[Optional[int], Optional[int]],
) -> str:
    clause = ""
    duration_min, duration_max = tests_duration
    if duration_min is not None:
        clause += (
            "AND ((tests.path like 'boot.%%' or tests.path = 'boot') "
            "OR tests.duration >= %(test_duration_min)s)\n"
        )
    if duration_max is not None:
        clause += (
            "AND ((tests.path like 'boot.%%' or tests.path = 'boot') "
            "OR tests.duration <= %(test_duration_max)s)\n"
        )
    duration_min, duration_max = boots_duration
    if duration_min is not None:
        clause += (
            "AND (NOT (tests.path like 'boot.%%' or tests.path = 'boot') "
            "OR tests.duration >= %(boot_duration_min)s)\n"
        )
    if duration_max is not None:
        clause += (
            "AND (NOT (tests.path like 'boot.%%' or tests.path = 'boot') "
            "OR tests.duration <= %(boot_duration_max)s)\n"
        )
    return clause
