"""Match a lab by labs.name via lab_id. Unknown means lab_id IS NULL.

A name that exists only in misc does not match. The displayed lab can still
fall back to misc; callers that filter in Python must pass lab_for_filter.
"""

import re
from typing import Optional

from kernelCI_app.constants.general import UNKNOWN_STRING


def _boot_path(column: str) -> str:
    """True only for boot and boot.* . NULL and bootloader are not boots."""
    path = f"COALESCE({column}, '')"
    return f"({path} = 'boot' OR {path} LIKE 'boot.%%')"


def as_positional(sql: str, params: dict) -> tuple[str, list]:
    values: list = []

    def replace(match: re.Match) -> str:
        values.append(params[match.group(1)])
        return "%s"

    return re.sub(r"%\((\w+)\)s", replace, sql), values


def lab_for_filter(lab_id, display_name: Optional[str]) -> str:
    """Lab string for the Python filter. NULL lab_id is Unknown, not the misc name."""
    if lab_id is None:
        return UNKNOWN_STRING
    # A present lab_id is not Unknown, even when the labs row has no name.
    return display_name or f"id:{lab_id}"


def lab_filter_sql(
    labs: Optional[set[str]],
    *,
    lab_id_column: str,
    param: str,
) -> tuple[str, dict]:
    """SQL predicate and params. Empty labs means no predicate."""
    if not labs:
        return "", {}
    names = sorted(lab for lab in labs if lab and lab != UNKNOWN_STRING)
    unknown = UNKNOWN_STRING in labs
    parts: list[str] = []
    params: dict = {}
    if names:
        params[param] = names
        parts.append(
            f"EXISTS (SELECT 1 FROM labs {param}_row "
            f"WHERE {param}_row.id = {lab_id_column} "
            f"AND {param}_row.name = ANY(%({param})s))"
        )
    if unknown:
        parts.append(f"{lab_id_column} IS NULL")
    if not parts:
        return "FALSE", {}
    if len(parts) == 1:
        return parts[0], params
    return "(" + " OR ".join(parts) + ")", params


def test_side_lab_sql(
    boot_labs: Optional[set[str]],
    test_labs: Optional[set[str]],
    *,
    table: str = "tests",
) -> tuple[str, dict]:
    """Predicate for a tests row: boot.lab on boot paths, test.lab on the rest."""
    boot_sql, boot_params = lab_filter_sql(
        boot_labs, lab_id_column=f"{table}.lab_id", param="boot_labs"
    )
    test_sql, test_params = lab_filter_sql(
        test_labs, lab_id_column=f"{table}.lab_id", param="test_labs"
    )
    if not boot_sql and not test_sql:
        return "", {}
    boot_ok = boot_sql or "TRUE"
    test_ok = test_sql or "TRUE"
    is_boot = _boot_path(f"{table}.path")
    return (
        f"(({is_boot} AND ({boot_ok})) OR (NOT {is_boot} AND ({test_ok})))",
        {**boot_params, **test_params},
    )


def hardware_details_lab_sql(
    *,
    scope: str,
    boot_labs: Optional[set[str]],
    test_labs: Optional[set[str]],
    build_labs: Optional[set[str]],
) -> tuple[str, dict]:
    """Lab predicate for one hardware details tab (build, boot, or test).

    The full page does not use this. It filters with full_page_lab_sql so the
    row kept for a build is one of the rows already in the hardware window.
    """
    boot_sql, boot_params = lab_filter_sql(
        boot_labs, lab_id_column="tests.lab_id", param="boot_labs"
    )
    test_sql, test_params = lab_filter_sql(
        test_labs, lab_id_column="tests.lab_id", param="test_labs"
    )
    build_sql, build_params = lab_filter_sql(
        build_labs, lab_id_column="builds.lab_id", param="build_labs"
    )
    if scope == "build":
        return build_sql, build_params
    is_boot = _boot_path("tests.path")
    if scope == "boot":
        if not boot_sql:
            return "", {}
        return f"({is_boot} AND {boot_sql})", boot_params
    if scope == "test":
        if not test_sql:
            return "", {}
        return f"(NOT {is_boot} AND {test_sql})", test_params

    # build.lab alone stays per tab on the shared query: filtering it here
    # would drop tests. The full page applies test.lab in full_page_lab_sql.
    return "", {}


def full_page_lab_sql(
    *,
    boot_labs: Optional[set[str]],
    test_labs: Optional[set[str]],
    build_labs: Optional[set[str]],
) -> tuple[str, dict]:
    """Keep matching tests, plus one hardware_rows row per build."""
    boot_sql, boot_params = lab_filter_sql(
        boot_labs, lab_id_column="lab_id", param="boot_labs"
    )
    test_sql, test_params = lab_filter_sql(
        test_labs, lab_id_column="lab_id", param="test_labs"
    )
    build_sql, build_params = lab_filter_sql(
        build_labs, lab_id_column="build_lab_id", param="build_labs"
    )
    if not boot_sql and not test_sql:
        return "", {}
    is_boot = _boot_path("path")
    path_ok = (
        f"(({is_boot} AND ({boot_sql or 'TRUE'})) "
        f"OR (NOT {is_boot} AND ({test_sql or 'TRUE'})))"
    )
    representative = (
        "id = (SELECT MIN(rep.id) FROM hardware_rows rep "
        "WHERE rep.build_id = hardware_rows.build_id)"
    )
    params = {**boot_params, **test_params}
    if build_sql:
        return (
            f"({path_ok} OR ({build_sql} AND {representative}))",
            {**params, **build_params},
        )
    return f"({path_ok} OR {representative})", params
