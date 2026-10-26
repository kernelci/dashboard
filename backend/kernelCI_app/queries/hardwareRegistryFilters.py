from dataclasses import astuple, dataclass
from datetime import datetime
from typing import Optional

from django.db import connection

_CATALOG_COLUMNS = (
    ("architecture", "proc.architecture"),
    ("processor", "proc.id"),
    ("platform_vendor", "plat.vendor_id"),
    ("silicon_vendor", "proc.vendor_id"),
    ("system_module", "plat.system_module_id"),
    ("form_factor", "plat.form_factor"),
    ("board_type", "plat.type"),
)

_CHECKOUT_JOIN = """
    INNER JOIN checkouts selected
        ON selected.id = daily.checkout_id
        AND selected.start_time >= %(start_date)s
        AND selected.start_time <= %(end_date)s
        AND (
            selected.git_commit_hash = ANY(%(commits_list)s)
            OR (
                selected.git_commit_tags IS NOT NULL
                AND selected.git_commit_tags && %(commits_list)s::text[]
            )
        )
"""


def normalize_csv(value: object) -> tuple[str, ...]:
    if not isinstance(value, str):
        return ()
    return tuple(part.strip() for part in value.split(",") if part.strip())


@dataclass(frozen=True)
class HardwareRegistryFilter:
    architecture: tuple[str, ...] = ()
    processor: tuple[str, ...] = ()
    platform_vendor: tuple[str, ...] = ()
    silicon_vendor: tuple[str, ...] = ()
    platform: tuple[str, ...] = ()
    system_module: tuple[str, ...] = ()
    form_factor: tuple[str, ...] = ()
    board_type: tuple[str, ...] = ()

    def is_empty(self) -> bool:
        return not any(astuple(self))


def hardware_registry_filter_from_request(params) -> HardwareRegistryFilter:
    return HardwareRegistryFilter(
        architecture=normalize_csv(params.get("architecture")),
        processor=normalize_csv(params.get("processor")),
        platform_vendor=normalize_csv(params.get("platformVendor")),
        silicon_vendor=normalize_csv(params.get("siliconVendor")),
        platform=normalize_csv(params.get("platform")),
        system_module=normalize_csv(params.get("systemModule")),
        form_factor=normalize_csv(params.get("formFactor")),
        board_type=normalize_csv(params.get("boardType")),
    )


def registry_filter_predicate(
    registry_filter: HardwareRegistryFilter, platform_sql: str
) -> tuple[Optional[str], dict]:
    """Same field is OR (`= ANY`). Different fields are AND.

    A platform missing from the registry matches only when the platform id
    is the sole selected field.
    """
    if registry_filter.is_empty():
        return None, {}

    platform_only = bool(registry_filter.platform) and all(
        not getattr(registry_filter, name) for name, _column in _CATALOG_COLUMNS
    )
    if platform_only:
        return (
            f"{platform_sql} = ANY(%(platform)s)",
            {"platform": list(registry_filter.platform)},
        )

    params: dict = {}
    catalog: list[str] = []
    for name, column in _CATALOG_COLUMNS:
        values = getattr(registry_filter, name)
        if values:
            params[name] = list(values)
            catalog.append(f"{column} = ANY(%({name})s)")
    if registry_filter.platform:
        params["platform"] = list(registry_filter.platform)
        catalog.append("plat.id = ANY(%(platform)s)")

    registered = f"""
        {platform_sql} IN (
            SELECT plat.id
            FROM hardware_registry_platforms plat
            INNER JOIN hardware_registry_processors proc
                ON proc.id = plat.processor_id
            WHERE {" AND ".join(catalog)}
        )
    """
    return registered, params


_REVISION_JOIN = """
    INNER JOIN checkouts revision
        ON revision.id = daily.checkout_id
        AND revision.tree_name = %(tree_name)s
        AND revision.git_repository_url = %(git_repository_url)s
        AND revision.git_repository_branch = %(git_repository_branch)s
        AND revision.git_commit_hash = %(git_commit_hash)s
"""

# Latest checkout of each tree for each platform this origin tested.
_LATEST_PLATFORM_CHECKOUTS = """
    SELECT DISTINCT ON (
        tests.platform,
        checkouts.tree_name,
        checkouts.git_repository_branch,
        checkouts.git_repository_url,
        checkouts.origin
    )
        tests.checkout_id,
        tests.platform
    FROM hardware_daily_tests tests
    INNER JOIN checkouts
        ON checkouts.id = tests.checkout_id
    WHERE tests.test_origin = %(origin)s
      AND tests.checkout_day >= %(start_day)s
      AND tests.checkout_day <= %(end_day)s
    ORDER BY
        tests.platform,
        checkouts.tree_name,
        checkouts.git_repository_branch,
        checkouts.git_repository_url,
        checkouts.origin,
        checkouts.start_time DESC
"""

_PICKED_JOIN = """
    INNER JOIN picked
        ON picked.checkout_id = daily.checkout_id
        AND picked.platform = daily.platform
"""


def _side_counts(
    *,
    rows_name: str,
    table: str,
    origin_sql: str,
    sums: str,
    commits: bool,
    revision: bool = False,
    extra_join: str = "",
) -> str:
    if revision:
        checkout_join = _REVISION_JOIN
        day_filter = ""
    else:
        checkout_join = _CHECKOUT_JOIN if commits else ""
        day_filter = """
              AND daily.checkout_day >= %(start_day)s
              AND daily.checkout_day <= %(end_day)s
        """
    return f"""
        {rows_name}_rows AS (
            SELECT daily.*
            FROM {table} daily
            {checkout_join}
            {extra_join}
            WHERE {origin_sql}
            {day_filter}
        ),
        {rows_name}_hardware AS (
            SELECT DISTINCT ON (platform) platform, compatibles
            FROM {rows_name}_rows
            WHERE compatibles IS NOT NULL
            ORDER BY platform, CARDINALITY(compatibles) DESC, compatibles
        ),
        {rows_name}_counts AS (
            SELECT
                daily.platform,
                hardware.compatibles AS hardware,
                {sums}
            FROM {rows_name}_rows daily
            LEFT JOIN {rows_name}_hardware hardware USING (platform)
            GROUP BY daily.platform, hardware.compatibles
        )
    """


def _daily_listing_query(*, commits: bool, revision: bool, where: str) -> str:
    latest = not commits and not revision
    return f"""
        WITH {f"picked AS ({_LATEST_PLATFORM_CHECKOUTS})," if latest else ""}
        {
        _side_counts(
            rows_name="build",
            table="hardware_daily_builds",
            origin_sql="daily.test_origin = %(origin)s",
            sums='''
                SUM(daily.build_pass) AS build_pass,
                SUM(daily.build_failed) AS build_failed,
                SUM(daily.build_inc) AS build_inc
            ''',
            commits=commits,
            revision=revision,
            extra_join=_PICKED_JOIN if latest else "",
        )
    },
        {
        _side_counts(
            rows_name="test",
            table="hardware_daily_tests",
            origin_sql="daily.test_origin = %(origin)s",
            sums='''
                SUM(daily.boot_pass) AS boot_pass,
                SUM(daily.boot_failed) AS boot_failed,
                SUM(daily.boot_inc) AS boot_inc,
                SUM(daily.test_pass) AS test_pass,
                SUM(daily.test_failed) AS test_failed,
                SUM(daily.test_inc) AS test_inc
            ''',
            commits=commits,
            revision=revision,
            extra_join=_PICKED_JOIN if latest else "",
        )
    }
        SELECT
            COALESCE(builds.platform, tests.platform) AS platform,
            COALESCE(tests.hardware, builds.hardware) AS hardware,
            COALESCE(builds.build_pass, 0),
            COALESCE(builds.build_failed, 0),
            COALESCE(builds.build_inc, 0),
            COALESCE(tests.boot_pass, 0),
            COALESCE(tests.boot_failed, 0),
            COALESCE(tests.boot_inc, 0),
            COALESCE(tests.test_pass, 0),
            COALESCE(tests.test_failed, 0),
            COALESCE(tests.test_inc, 0)
        FROM build_counts builds
        FULL OUTER JOIN test_counts tests ON tests.platform = builds.platform
        {where}
        ORDER BY platform
    """


def _filter_clause(
    registry_filter: Optional[HardwareRegistryFilter],
) -> tuple[str, dict]:
    predicate, params = registry_filter_predicate(
        registry_filter or HardwareRegistryFilter(),
        "COALESCE(builds.platform, tests.platform)",
    )
    if not predicate:
        return "", params
    return f"WHERE {predicate}", params


def get_hardware_daily_listing(
    *,
    origin: str,
    start_date: datetime,
    end_date: datetime,
    commits_list: Optional[list[str]] = None,
    registry_filter: Optional[HardwareRegistryFilter] = None,
) -> list[tuple]:
    where, filter_params = _filter_clause(registry_filter)
    query = _daily_listing_query(
        commits=bool(commits_list), revision=False, where=where
    )
    with connection.cursor() as cursor:
        cursor.execute(
            query,
            {
                "origin": origin,
                "start_date": start_date,
                "end_date": end_date,
                "start_day": start_date.date(),
                "end_day": end_date.date(),
                "commits_list": commits_list,
                **filter_params,
            },
        )
        return cursor.fetchall()


def get_hardware_daily_revision_listing(
    *,
    origin: str,
    tree_name: str,
    git_repository_url: str,
    git_repository_branch: str,
    git_commit_hash: str,
    registry_filter: Optional[HardwareRegistryFilter] = None,
) -> list[tuple]:
    """Daily counts for one checkout. Same rows the revision filter options use."""
    where, filter_params = _filter_clause(registry_filter)
    query = _daily_listing_query(commits=False, revision=True, where=where)
    with connection.cursor() as cursor:
        cursor.execute(
            query,
            {
                "origin": origin,
                "tree_name": tree_name,
                "git_repository_url": git_repository_url,
                "git_repository_branch": git_repository_branch,
                "git_commit_hash": git_commit_hash,
                **filter_params,
            },
        )
        return cursor.fetchall()


def get_hardware_registry_filter_options(
    *,
    origin: str,
    start_date: datetime,
    end_date: datetime,
    tree_name: Optional[str] = None,
    git_repository_url: Optional[str] = None,
    git_repository_branch: Optional[str] = None,
    git_commit_hash: Optional[str] = None,
) -> dict[str, list[str]]:
    """Distinct registry values for the platforms in the current listing.

    Without a revision, each platform keeps the latest checkout of each tree
    in the window. With one, it is that checkout.
    Platform ids include boards that are not in the registry. The other lists
    do not: those boards have no architecture, vendor, or board type to offer.
    """
    revision = all(
        (
            tree_name,
            git_repository_url,
            git_repository_branch,
            git_commit_hash,
        )
    )
    if revision:
        picked = ""
        seen = f"""
            SELECT DISTINCT daily.platform
            FROM hardware_daily_tests daily
            {_REVISION_JOIN}
            WHERE daily.test_origin = %(origin)s
        """
    else:
        picked = f"picked AS ({_LATEST_PLATFORM_CHECKOUTS}),"
        seen = "SELECT DISTINCT platform FROM picked"
    query = f"""
        WITH {picked}
        seen AS (
            {seen}
        ),
        registered AS (
            SELECT
                plat.id,
                plat.vendor_id AS platform_vendor,
                plat.type AS board_type,
                plat.form_factor,
                plat.system_module_id AS system_module,
                proc.id AS processor,
                proc.architecture,
                proc.vendor_id AS silicon_vendor
            FROM seen
            INNER JOIN hardware_registry_platforms plat ON plat.id = seen.platform
            INNER JOIN hardware_registry_processors proc
                ON proc.id = plat.processor_id
        )
        SELECT
            ARRAY(
                SELECT DISTINCT architecture FROM registered
                WHERE architecture IS NOT NULL AND architecture <> ''
                ORDER BY 1
            ),
            ARRAY(SELECT DISTINCT processor FROM registered ORDER BY 1),
            ARRAY(SELECT DISTINCT platform_vendor FROM registered ORDER BY 1),
            ARRAY(SELECT DISTINCT silicon_vendor FROM registered ORDER BY 1),
            ARRAY(SELECT platform FROM seen ORDER BY 1),
            ARRAY(
                SELECT DISTINCT system_module FROM registered
                WHERE system_module IS NOT NULL AND system_module <> ''
                ORDER BY 1
            ),
            ARRAY(
                SELECT DISTINCT form_factor FROM registered
                WHERE form_factor IS NOT NULL AND form_factor <> ''
                ORDER BY 1
            ),
            ARRAY(
                SELECT DISTINCT board_type FROM registered
                WHERE board_type IS NOT NULL AND board_type <> ''
                ORDER BY 1
            )
    """
    params = {
        "origin": origin,
        "start_day": start_date.date(),
        "end_day": end_date.date(),
        "tree_name": tree_name,
        "git_repository_url": git_repository_url,
        "git_repository_branch": git_repository_branch,
        "git_commit_hash": git_commit_hash,
    }
    names = (
        "architecture",
        "processor",
        "platform_vendor",
        "silicon_vendor",
        "platform",
        "system_module",
        "form_factor",
        "board_type",
    )
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        row = cursor.fetchone()
    return {name: list(row[index] or []) for index, name in enumerate(names)}
