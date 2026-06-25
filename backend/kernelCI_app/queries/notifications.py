import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, time, timedelta, timezone
from typing import Any

from django.db import connection, connections
from pydantic import ValidationError

from kernelCI_app.cache import get_query_cache, set_query_cache
from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.helpers.logger import out
from kernelCI_app.queries.tree import get_tree_listing_query
from kernelCI_app.typeModels.metrics_notifications import (
    BuildIncidentsCount,
    LabMetricsData,
    MetricsReportData,
    TopIssue,
)

METRICS_CACHE_WARM_PERIODS = (7, 14)
METRICS_CACHE_TIMEOUT = 60 * 60 * 6  # 6 hours
METRICS_CACHE_WARM_TIMEOUT = 60 * 60 * 24 * 8  # 8 days


def kcidb_execute_query(query, params=None):
    try:
        with connection.cursor() as cur:
            # print(cur.mogrify(query, params))
            cur.execute(query, params)
            rows = cur.fetchall()
            if not rows:
                return []

            col_names = [desc[0] for desc in cur.description]
            result = []
            for row in rows:
                row_dict = dict(zip(col_names, row, strict=False))
                result.append(row_dict)

            return result
    except Exception as e:
        print(f"Query execution failed: {e}")
        sys.exit()


def kcidb_new_issues():
    """Fetch issues from the last few days, including related checkouts."""

    params = {"interval": "1 hour"}

    query = """
        WITH ranked_issues AS (
        SELECT
            i._timestamp,
            i.id,
            i.version,
            i.comment,
            i.misc,
            i.origin,
            ROW_NUMBER() OVER (PARTITION BY i.id ORDER BY i.version DESC) AS rn
        FROM
            public.issues i
        WHERE i._timestamp >= NOW() - INTERVAL %(interval)s
        ),

        highest_version AS (
        SELECT
            _timestamp,
            id,
            version,
            comment,
            misc,
            origin
        FROM
            ranked_issues
        WHERE
            rn = 1 -- Keep only the highest version for each id
        ),

        older_issues AS (
        SELECT
            h._timestamp,
            h.id,
            h.version,
            h.comment,
            h.misc,
            h.origin
        FROM highest_version h
        LEFT JOIN incidents inc
            ON h.id = inc.issue_id
        WHERE inc._timestamp < NOW() - INTERVAL %(interval)s
        ),

        new_issues AS (
            SELECT * FROM highest_version
            EXCEPT
            SELECT * FROM older_issues
        ),

        first_incidents AS (
           SELECT
               inc._timestamp,
               inc.issue_id,
               inc.issue_version,
               inc.test_id,
               inc.build_id,
               c.git_repository_url,
               c.tree_name,
               c.git_repository_branch,
               c.git_commit_hash,
               c.git_commit_name,
               ROW_NUMBER() OVER (PARTITION BY inc.issue_id ORDER BY inc._timestamp ASC) as incident_rn
           FROM incidents inc
           JOIN builds b ON inc.build_id = b.id
           JOIN checkouts c ON b.checkout_id = c.id
           WHERE inc._timestamp >= NOW() - INTERVAL %(interval)s

           UNION

           SELECT
               inc._timestamp,
               inc.issue_id,
               inc.issue_version,
               inc.test_id,
               inc.build_id,
               c.git_repository_url,
               c.tree_name,
               c.git_repository_branch,
               c.git_commit_hash,
               c.git_commit_name,
               ROW_NUMBER() OVER (PARTITION BY inc.issue_id ORDER BY inc._timestamp ASC) as incident_rn
           FROM incidents inc
           JOIN tests t ON inc.test_id = t.id
           JOIN builds b ON t.build_id = b.id
           JOIN checkouts c ON b.checkout_id = c.id
           WHERE inc._timestamp >= NOW() - INTERVAL %(interval)s
            AND (t.path = 'boot' OR t.path = 'boot.nfs')
       )

        SELECT
            fi._timestamp,
            n.id,
            n.version,
            n.comment,
            n.origin,
            fi.build_id,
            fi.test_id,
            n.misc,
            fi.git_repository_url,
            fi.tree_name,
            fi.git_repository_branch,
            fi.git_commit_hash,
            fi.git_commit_name,
            COUNT(inc.id) AS incident_count
        FROM new_issues n
        LEFT JOIN first_incidents fi ON n.id = fi.issue_id AND fi.incident_rn = 1
        LEFT JOIN incidents inc ON n.id = inc.issue_id
        GROUP BY  -- Important: Group by all selected columns *except* the count
            fi._timestamp,
            n.id,
            n.version,
            n.comment,
            n.origin,
            fi.build_id,
            fi.test_id,
            n.misc,
            fi.git_repository_url,
            fi.tree_name,
            fi.git_repository_branch,
            fi.git_commit_hash,
            fi.git_commit_name
        ORDER BY fi._timestamp DESC;
        """

    return kcidb_execute_query(query, params)


# TODO: include issue version as an optional parameter
def kcidb_issue_details(issue_id):
    """Fetches details of a given issue."""

    params = {"issue_id": issue_id}

    query = """
        WITH our_issue AS (
            SELECT *
            FROM issues
            WHERE id = %(issue_id)s
            ORDER BY version DESC
            LIMIT 1
        ),
        first_incidents AS (
           SELECT
               inc.issue_id,
               inc.issue_version,
               inc.test_id,
               inc.build_id,
               c.git_repository_url,
               c.tree_name,
               c.git_repository_branch,
               c.git_commit_hash,
               c.git_commit_name,
               c.git_commit_tags,
               ROW_NUMBER() OVER (PARTITION BY inc.issue_id ORDER BY inc._timestamp ASC) as incident_rn
           FROM incidents inc
           JOIN builds b ON inc.build_id = b.id
           JOIN checkouts c ON b.checkout_id = c.id
           WHERE inc.issue_id = %(issue_id)s

           UNION

           SELECT
               inc.issue_id,
               inc.issue_version,
               inc.test_id,
               inc.build_id,
               c.git_repository_url,
               c.tree_name,
               c.git_repository_branch,
               c.git_commit_hash,
               c.git_commit_name,
               c.git_commit_tags,
               ROW_NUMBER() OVER (PARTITION BY inc.issue_id ORDER BY inc._timestamp ASC) as incident_rn
           FROM incidents inc
           JOIN tests t ON inc.test_id = t.id
           JOIN builds b ON t.build_id = b.id
           JOIN checkouts c ON b.checkout_id = c.id
           WHERE inc.issue_id = %(issue_id)s
       )

        SELECT
            n._timestamp,
            n.id,
            n.version,
            n.comment,
            fi.build_id,
            fi.test_id,
            n.misc,
            fi.git_repository_url,
            fi.tree_name,
            fi.git_repository_branch,
            fi.git_commit_hash,
            fi.git_commit_name,
            fi.git_commit_tags,
            COUNT(inc.id) AS incident_count
        FROM our_issue n
        LEFT JOIN first_incidents fi ON n.id = fi.issue_id AND fi.incident_rn = 1
        LEFT JOIN incidents inc ON n.id = inc.issue_id
        GROUP BY  -- Important: Group by all selected columns *except* the count
            n._timestamp,
            n.id,
            n.version,
            n.comment,
            fi.build_id,
            fi.test_id,
            n.misc,
            fi.git_repository_url,
            fi.tree_name,
            fi.git_repository_branch,
            fi.git_commit_hash,
            fi.git_commit_name,
            fi.git_commit_tags
    """

    return kcidb_execute_query(query, params)


def kcidb_build_incidents(issue_id):
    """Fetches build incidents of a given issue."""

    params = {"issue_id": issue_id}

    query = """
        SELECT DISTINCT ON (b.config_name, b.architecture, b.compiler)
            b.id,
            b.config_name,
            b.config_url,
            b.architecture,
            b.compiler
        FROM builds b
            LEFT JOIN incidents inc ON inc.build_id = b.id
        WHERE inc.issue_id = %(issue_id)s
        ORDER BY b.config_name, b.architecture, b.compiler, b._timestamp DESC;
    """

    return kcidb_execute_query(query, params)


def kcidb_test_incidents(issue_id):
    """Fetches test incidents of a given issue."""

    params = {"issue_id": issue_id}

    query = """
        WITH ranked_tests AS (
            SELECT
                t.id,
                t._timestamp,
                t.path,
                t.environment_compatible,
                t.environment_misc->>'platform' AS platform,
                COUNT(*) OVER (PARTITION BY t.environment_misc->>'platform') AS platform_count,
                ROW_NUMBER() OVER
                    (PARTITION BY t.environment_misc->>'platform' ORDER BY t._timestamp ASC) AS rn_oldest
            FROM tests t
            LEFT JOIN incidents inc ON inc.test_id = t.id
            WHERE inc.issue_id = %(issue_id)s
                 AND (t.path = 'boot' OR t.path = 'boot.nfs')
        ),

        oldest_timestamps AS ( -- CTE to get the oldest timestamps
            SELECT
                platform,
                _timestamp AS oldest_timestamp
            FROM ranked_tests
            WHERE rn_oldest = 1 -- Oldest test for each platform
        )

        SELECT DISTINCT ON (platform)
            rt.*,
            ot.oldest_timestamp
        FROM ranked_tests rt
        JOIN (SELECT platform, platform_count from ranked_tests) pc ON rt.platform = pc.platform
        JOIN oldest_timestamps ot ON rt.platform = ot.platform
        ORDER BY platform, _timestamp DESC;
    """

    return kcidb_execute_query(query, params)


def kcidb_last_test_without_issue(issue, incident):
    """Fetches build incidents of a given issue."""

    params = {
        "origin": "maestro",
        "issue_id": issue["id"],
        "path": incident["path"],
        "platform": incident["platform"],
        "timestamp": incident["oldest_timestamp"],
        "giturl": issue["git_repository_url"],
        "branch": issue["git_repository_branch"],
        "interval": "18 days",
    }

    query = """
    WITH tests_with_issue AS (
        SELECT DISTINCT c.git_commit_hash
        FROM tests t
        JOIN builds b ON t.build_id = b.id
        JOIN checkouts c ON b.checkout_id = c.id
        JOIN incidents inc ON inc.test_id = t.id
        WHERE inc.issue_id = %(issue_id)s
     )
    SELECT t.id, t.start_time, c.git_commit_hash
        FROM tests t
        JOIN builds b ON t.build_id = b.id
        JOIN checkouts c ON b.checkout_id = c.id
        WHERE c.git_repository_url = %(giturl)s
        AND c.git_repository_branch = %(branch)s
        AND t.environment_misc->>'platform' = %(platform)s
        AND t.path = %(path)s
        AND t.status = 'PASS'
        AND c.origin = %(origin)s
        AND t._timestamp >= NOW() - INTERVAL %(interval)s
        AND c.git_commit_hash NOT IN
            (
                SELECT git_commit_hash FROM tests_with_issue
            )
        ORDER BY b.start_time DESC
        LIMIT 1;
    """

    return kcidb_execute_query(query, params)


def kcidb_last_build_without_issue(issue, incident):
    """Fetches the last successful build of the same config that does not carry
    the given issue, used to bound the regression range for regzbot."""

    params = {
        "origin": "maestro",
        "issue_id": issue["id"],
        "config_name": incident["config_name"],
        "architecture": incident["architecture"],
        "compiler": incident["compiler"],
        "giturl": issue["git_repository_url"],
        "branch": issue["git_repository_branch"],
        "interval": "18 days",
    }

    query = """
    WITH builds_with_issue AS (
        SELECT DISTINCT c.git_commit_hash
        FROM builds b
        JOIN checkouts c ON b.checkout_id = c.id
        JOIN incidents inc ON inc.build_id = b.id
        WHERE inc.issue_id = %(issue_id)s
     )
    SELECT b.id, b.start_time, c.git_commit_hash
        FROM builds b
        JOIN checkouts c ON b.checkout_id = c.id
        WHERE c.git_repository_url = %(giturl)s
        AND c.git_repository_branch = %(branch)s
        AND b.config_name = %(config_name)s
        AND b.architecture = %(architecture)s
        AND b.compiler = %(compiler)s
        AND b.status = 'PASS'
        AND c.origin = %(origin)s
        AND b.start_time >= NOW() - INTERVAL %(interval)s
        AND c.git_commit_hash NOT IN
            (
                SELECT git_commit_hash FROM builds_with_issue
            )
        ORDER BY b.start_time DESC
        LIMIT 1;
    """

    return kcidb_execute_query(query, params)


# Similar to the tree listing summary query, but with notification-specific filters.
# Only the "with", "join" and "where" clauses change
def get_checkout_summary_data(
    *,
    tuple_params: list[tuple[str, str, str]],
    interval_min="5 hours",
    interval_max="29 hours",
) -> list[dict]:
    """Queries for the checkout and status count data similarly to tree_listing but
    using a list of parameters for the filtering

    Parameters:
        tuple_params: a list of tuples (str, str, str)
        representing (git_repository_branch, git_repository_url, origin)

    Returns:
        out: a list of dicts with the records found.
        If no tuple parameters are provided, returns an empty list
    """
    if not tuple_params:
        return []

    with_clause = f"""
            WITH
                ORDERED_CHECKOUTS_BY_TREE AS (
                    SELECT
                        C.GIT_REPOSITORY_BRANCH,
                        C.GIT_REPOSITORY_URL,
                        C.GIT_COMMIT_HASH,
                        C.ORIGIN,
                        ROW_NUMBER() OVER (
                            PARTITION BY
                                C.GIT_REPOSITORY_BRANCH,
                                C.GIT_REPOSITORY_URL
                            ORDER BY
                                C.START_TIME DESC
                        ) AS TIME_ORDER
                    FROM
                        CHECKOUTS C
                    JOIN (
                        VALUES
                            {",".join(["(%s, %s, %s)"] * len(tuple_params))}
                        ) AS v(branch, giturl, origin)
                        ON (
                            c.git_repository_branch = v.branch
                            AND c.git_repository_url = v.giturl
                            AND c.origin = v.origin
                        )
                    WHERE
                        C.START_TIME >= NOW() - INTERVAL %s
                        AND C.START_TIME <= NOW() - INTERVAL %s
                ),
                FIRST_TREE_CHECKOUT AS (
                    SELECT
                        GIT_REPOSITORY_BRANCH,
                        GIT_REPOSITORY_URL,
                        GIT_COMMIT_HASH,
                        ORIGIN
                    FROM
                        ORDERED_CHECKOUTS_BY_TREE
                    WHERE
                        TIME_ORDER = 1
                )
    """

    join_clause = """
                JOIN FIRST_TREE_CHECKOUT FTC ON (
                    checkouts.git_repository_branch IS NOT DISTINCT FROM FTC.GIT_REPOSITORY_BRANCH
                    AND checkouts.git_repository_url IS NOT DISTINCT FROM FTC.GIT_REPOSITORY_URL
                    AND checkouts.git_commit_hash = FTC.GIT_COMMIT_HASH
                    AND checkouts.origin = FTC.ORIGIN
                )
    """

    query = get_tree_listing_query(
        with_clause=with_clause,
        join_clause=join_clause,
        where_clause="",
    )

    flattened_list = []
    for tuple in tuple_params:
        flattened_list += list(tuple)

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            flattened_list
            + [
                interval_max,
                interval_min,
            ],
        )
        return dict_fetchall(cursor=cursor)


def kcidb_tests_results(
    *,
    origin: str,
    giturl: str,
    branch: str,
    hash: str,
    paths: list[str],
    interval: str,
    group_size: int,
):
    """Fetches the n-test history of searched tests in a specific tree.

    This query:
        - Gathers data for the tree (origin, url, branch) at every checkout prior to the searched hash;
        - Adds a row number to the data grouping by test path, test platform and build config_name,
          ordering by the test start_time;
        - Limits to n tests on that history grouping;
        - Limits only to tests that had the latest occurence in the searched hash.

    Args:
        origin: The origin to filter by
        giturl: The git repository URL
        branch: The git repository branch
        hash: The git commit hash
        path: An array of strings representing test paths to match (using LIKE)
        interval: Time interval for filtering (such as '7 days' or '12 hours')
        group_size: Maximum number of tests to return per group
    """

    path_params = {}
    if not paths:
        path_clause = ""
    elif len(paths) == 1:
        path_clause = "AND t.path LIKE %(path)s"
        path_params["path"] = paths[0]
    else:
        path_clause_keys = []
        for idx, path in enumerate(paths):
            query_key = f"path_{idx}"
            path_params[query_key] = path
            path_clause_keys.append(f"%({query_key})s")
        path_clause_keys_full = " OR t.path LIKE ".join(path_clause_keys)

        path_clause = "AND (t.path LIKE " + path_clause_keys_full + ")"

    params = {
        "origin": origin,
        "giturl": giturl,
        "branch": branch,
        "hash": hash,
        "interval": interval,
        "group_size": group_size,
        **path_params,
    }

    query = f"""
        WITH
            prefiltered_data AS (
                SELECT
                    t.id,
                    t.path,
                    t.status,
                    t.start_time,
                    t.environment_misc->>'platform' AS platform,
                    b.architecture,
                    b.compiler,
                    b.config_name,
                    c.git_commit_hash
                FROM tests t
                    JOIN builds b ON t.build_id = b.id
                    JOIN checkouts c ON b.checkout_id = c.id
                WHERE t.origin = %(origin)s
                    AND c.git_repository_url = %(giturl)s
                    AND c.git_repository_branch = %(branch)s
                    {path_clause}
                    AND t.environment_misc->>'platform' != 'kubernetes'
                    AND C.start_time <= (
                        SELECT
                            MAX(start_time)
                        FROM
                            checkouts
                        WHERE
                            git_commit_hash = %(hash)s
                    )
                    AND c.start_time >= NOW() - INTERVAL %(interval)s
                    AND b.start_time >= NOW() - INTERVAL %(interval)s
                    AND t.start_time >= NOW() - INTERVAL %(interval)s
            ),
            ranked_data AS (
                SELECT
                    *,
                    -- Using the same PARTITION BY in both window functions
                    -- may allow the query optimizer to reuse partitioning
                    ROW_NUMBER() OVER (
                        PARTITION BY
                            path,
                            platform,
                            config_name,
                            architecture,
                            compiler
                        ORDER BY
                            start_time DESC NULLS LAST
                    ) AS rn,
                    FIRST_VALUE(git_commit_hash) OVER (
                        PARTITION BY
                            path,
                            platform,
                            config_name,
                            architecture,
                            compiler
                        ORDER BY
                            start_time DESC NULLS LAST
                    ) AS first_hash_by_group
                FROM
                    prefiltered_data
            )
        SELECT
            id,
            path,
            status,
            start_time,
            platform,
            architecture,
            compiler,
            config_name,
            git_commit_hash,
            rn
        FROM
            ranked_data
        WHERE
            rn <= %(group_size)s
            AND first_hash_by_group = %(hash)s
        ORDER BY
            path,
            platform,
            config_name,
            architecture,
            compiler,
            start_time DESC NULLS LAST;
        """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        # TODO: check if it is possible to remove dict_fetchall.
        # dict_fetchall has a performance impact and this query returns many rows,
        # so they shouldn't be together
        return dict_fetchall(cursor=cursor)


def get_issues_summary_data(*, checkout_ids: list[str]) -> list[dict]:
    if not checkout_ids:
        return []

    query = f"""
        SELECT DISTINCT
            b.checkout_id,
            b.id as build_id,
            inc.issue_id,
            inc.issue_version,
            i.report_url,
            i.culprit_code,
            i.culprit_tool,
            i.culprit_harness,
            i.origin,
            i.comment
        FROM
            builds b
        LEFT JOIN incidents inc
            ON b.id = inc.build_id
        LEFT JOIN issues i
            ON inc.issue_id = i.id AND inc.issue_version = i.version
        WHERE
            b.checkout_id IN ({", ".join(["%s"] * len(checkout_ids))}) and b.status = 'FAIL'
        ORDER BY issue_id
    """

    with connections["default"].cursor() as cursor:
        cursor.execute(query, checkout_ids)
        return dict_fetchall(cursor=cursor)


def query_fetchone_work(
    *,
    cache_key: str,
    query: str,
    params: dict[str, Any],
    timeout: int = METRICS_CACHE_TIMEOUT,
    use_cache: bool = True,
) -> Any:
    if use_cache:
        cached = get_query_cache(key=cache_key, params=params)
        if cached is not None:
            return cached
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchone()
    finally:
        connections["default"].close()
    set_query_cache(
        key=cache_key,
        params=params,
        rows=rows,
        timeout=timeout,
    )
    return rows


def query_fetchall_work(
    *,
    cache_key: str,
    query: str,
    params: dict[str, Any],
    timeout: int = METRICS_CACHE_TIMEOUT,
    use_cache: bool = True,
) -> Any:
    if use_cache:
        cached = get_query_cache(key=cache_key, params=params)
        if cached is not None:
            return cached
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
    finally:
        connections["default"].close()
    set_query_cache(
        key=cache_key,
        params=params,
        rows=rows,
        timeout=timeout,
    )
    return rows


def last_saturday(today: date | None = None) -> date:
    """Most recent Saturday UTC (today when today is Saturday)."""
    day = today or datetime.now(timezone.utc).date()
    return day - timedelta(days=(day.weekday() + 2) % 7)


def interval_params(start_days_ago: int, end_days_ago: int) -> dict[str, str]:
    """Build [start_date, end_date) bounds from UTC day offsets."""
    today = datetime.now(timezone.utc).date()
    start_datetime = datetime.combine(
        today - timedelta(days=start_days_ago), time.min, tzinfo=timezone.utc
    )
    end_datetime = datetime.combine(
        today - timedelta(days=end_days_ago),
        time.min,
        tzinfo=timezone.utc,
    )
    return {
        "start_date": start_datetime.isoformat(),
        "end_date": end_datetime.isoformat(),
    }


def get_metrics_data(
    *,
    start_days_ago: int,
    end_days_ago: int,
    use_cache: bool = True,
    cache_timeout: int = METRICS_CACHE_TIMEOUT,
) -> MetricsReportData:

    if start_days_ago > 30:
        out(
            "Warning: metrics report for more than 30 days may take a long time to generate."
        )

    period_length = end_days_ago - start_days_ago
    prev_start_days_ago = start_days_ago - period_length
    prev_end_days_ago = start_days_ago

    params = interval_params(start_days_ago, end_days_ago)
    prev_params = interval_params(prev_start_days_ago, prev_end_days_ago)

    total_objects_query = """
    SELECT
        c.n_trees,
        c.n_checkouts,
        (SELECT COUNT(*) FROM builds WHERE _timestamp >=
            %(start_date)s::timestamptz
            AND _timestamp < %(end_date)s::timestamptz)
            AS n_builds,
        (SELECT COUNT(*) FROM tests WHERE _timestamp >=
            %(start_date)s::timestamptz
            AND _timestamp < %(end_date)s::timestamptz)
            AS n_tests,
        (SELECT COUNT(*) FROM issues WHERE _timestamp >=
            %(start_date)s::timestamptz
            AND _timestamp < %(end_date)s::timestamptz)
            AS n_issues,
        (SELECT COUNT(*) FROM incidents WHERE _timestamp >=
            %(start_date)s::timestamptz
            AND _timestamp < %(end_date)s::timestamptz)
            AS n_incidents
    FROM (
        SELECT
            COUNT(DISTINCT tree_name) AS n_trees,
            COUNT(*) AS n_checkouts
        FROM checkouts
        WHERE _timestamp >= %(start_date)s::timestamptz
            AND _timestamp < %(end_date)s::timestamptz
    ) c;
    """

    build_incidents_query = """
    -- Ranks incidents of each issue by time to check which incident was the first incident of an issue
    WITH time_rank AS (
        SELECT
            _timestamp,
            origin,
            issue_id,
            ROW_NUMBER() OVER (PARTITION BY issue_id ORDER BY _timestamp) AS rn
        FROM incidents
            where build_id is not null
    ),
    -- counts total incidents in interval and how many were the first incident of an issue
    numbers AS (
        SELECT
            origin,
            COUNT(*) FILTER (
                WHERE _timestamp >= %(start_date)s::timestamptz AND _timestamp < %(end_date)s::timestamptz
            ) AS total_incidents,
            COUNT(*) FILTER (
                WHERE _timestamp >= %(start_date)s::timestamptz AND _timestamp < %(end_date)s::timestamptz
                AND rn = 1
            ) AS n_new_issues,
            COUNT(DISTINCT issue_id) FILTER (
                WHERE _timestamp >= %(start_date)s::timestamptz AND _timestamp < %(end_date)s::timestamptz
            ) AS n_issues
        FROM time_rank
        GROUP BY origin
    ),
    -- counts incidents by issue
    grouped_counted AS (
        SELECT
            inc.origin,
            inc.issue_id,
            inc.issue_version,
            i.comment,
            COUNT(inc.*) AS total
        FROM incidents inc
        JOIN issues i ON inc.issue_id = i.id AND inc.issue_version = i.version
        WHERE
            inc.build_id is not null
            AND inc._timestamp >=
                %(start_date)s::timestamptz
                AND inc._timestamp < %(end_date)s::timestamptz
        GROUP BY inc.origin, inc.issue_id, inc.issue_version, i.comment
        ORDER BY inc.origin, total DESC
    ),
    -- ranks issues by number of incidents
    ranked_counted AS (
        SELECT
            *,
            ROW_NUMBER() OVER (PARTITION BY origin ORDER BY total DESC) as ranked
        FROM grouped_counted
    )
    -- combines data into single output,
    -- repeating total incidents by origin and adding the top 3 issues per origin
    SELECT
        n.origin,
        n.total_incidents,
        n.n_new_issues,
        n.n_issues,
        r.issue_id,
        r.issue_version,
        r.comment,
        r.total
    FROM numbers n
    JOIN ranked_counted r
    ON n.origin = r.origin
    WHERE r.ranked <= 3 AND n.total_incidents > 0
    """

    new_build_issues_query = """
    WITH time_rank AS (
        SELECT
            _timestamp,
            origin,
            issue_id,
            ROW_NUMBER() OVER (PARTITION BY issue_id ORDER BY _timestamp) AS rn
        FROM incidents
        WHERE build_id IS NOT NULL
    ),
    new_issues AS (
        SELECT issue_id, origin
        FROM time_rank
        WHERE rn = 1
            AND _timestamp >= %(start_date)s::timestamptz AND _timestamp < %(end_date)s::timestamptz
    )
    SELECT
        inc.origin,
        inc.issue_id,
        inc.issue_version,
        i.comment,
        COUNT(inc.*) AS total
    FROM incidents inc
    JOIN issues i ON inc.issue_id = i.id AND inc.issue_version = i.version
    JOIN new_issues ni ON inc.issue_id = ni.issue_id AND inc.origin = ni.origin
    WHERE
        inc.build_id IS NOT NULL
        AND inc._timestamp >=
            %(start_date)s::timestamptz
            AND inc._timestamp < %(end_date)s::timestamptz
    GROUP BY inc.origin, inc.issue_id, inc.issue_version, i.comment
    ORDER BY inc.origin, total DESC
    """

    lab_summary_query = """
    -- get count of tests of each lab and how many builds are related to those tests
    SELECT
        t.misc->>'runtime' AS lab,
        COUNT(DISTINCT t.build_id) AS n_builds,
        COUNT(*) FILTER (WHERE t.path LIKE 'boot.%%' OR t.path = 'boot') AS n_boots,
        COUNT(*) FILTER (WHERE t.path NOT LIKE 'boot.%%' AND t.path != 'boot') AS n_tests
    FROM tests t
    WHERE
        t.misc->>'runtime' IS NOT NULL
        AND t._timestamp >=
            %(start_date)s::timestamptz
            AND t._timestamp < %(end_date)s::timestamptz
    GROUP BY lab
    """

    with ThreadPoolExecutor(max_workers=6) as executor:
        total_objects_result = executor.submit(
            query_fetchone_work,
            cache_key="metricsTotalObjects",
            query=total_objects_query,
            params=params,
            use_cache=use_cache,
            timeout=cache_timeout,
        )
        prev_total_objects_result = executor.submit(
            query_fetchone_work,
            cache_key="metricsTotalObjects",
            query=total_objects_query,
            params=prev_params,
            use_cache=use_cache,
            timeout=cache_timeout,
        )
        build_incidents_result = executor.submit(
            query_fetchall_work,
            cache_key="metricsBuildIncidents",
            query=build_incidents_query,
            params=params,
            use_cache=use_cache,
            timeout=cache_timeout,
        )
        new_build_issues_result = executor.submit(
            query_fetchall_work,
            cache_key="metricsNewBuildIssues",
            query=new_build_issues_query,
            params=params,
            use_cache=use_cache,
            timeout=cache_timeout,
        )
        lab_summary_results = executor.submit(
            query_fetchall_work,
            cache_key="metricsLabSummary",
            query=lab_summary_query,
            params=params,
            use_cache=use_cache,
            timeout=cache_timeout,
        )
        prev_lab_summary_results = executor.submit(
            query_fetchall_work,
            cache_key="metricsLabSummary",
            query=lab_summary_query,
            params=prev_params,
            use_cache=use_cache,
            timeout=cache_timeout,
        )

    total_objects_result = total_objects_result.result()
    prev_total_objects_result = prev_total_objects_result.result()
    build_incidents_result = build_incidents_result.result()
    new_build_issues_result = new_build_issues_result.result()
    lab_summary_results = lab_summary_results.result()
    prev_lab_summary_results = prev_lab_summary_results.result()

    try:
        build_incidents_by_origin: dict[str, BuildIncidentsCount] = {}
        top_issues_by_origin: dict[str, dict[tuple[str, int], TopIssue]] = {}
        new_issues_by_origin: dict[str, dict[tuple[str, int], TopIssue]] = {}
        for row in build_incidents_result:
            origin = row[0]
            issue_id = row[4]
            issue_version = row[5]
            build_incidents_by_origin[origin] = BuildIncidentsCount(
                total_incidents=row[1],
                n_new_issues=row[2],
                n_total_issues=row[3],
                n_existing_issues=row[3] - row[2],
            )
            if top_issues_by_origin.get(origin) is None:
                top_issues_by_origin[origin] = {}
            top_issues_by_origin[origin][(issue_id, issue_version)] = TopIssue(
                id=issue_id,
                version=issue_version,
                comment=row[6],
                total_incidents=row[7],
            )

        for row in new_build_issues_result:
            origin = row[0]
            issue_id = row[1]
            issue_version = row[2]
            if new_issues_by_origin.get(origin) is None:
                new_issues_by_origin[origin] = {}
            new_issues_by_origin[origin][(issue_id, issue_version)] = TopIssue(
                id=issue_id,
                version=issue_version,
                comment=row[3],
                total_incidents=row[4],
            )

        data = MetricsReportData(
            n_trees=total_objects_result[0],
            n_checkouts=total_objects_result[1],
            n_builds=total_objects_result[2],
            n_tests=total_objects_result[3],
            n_issues=total_objects_result[4],
            n_incidents=total_objects_result[5],
            build_incidents_by_origin=build_incidents_by_origin,
            top_issues_by_origin=top_issues_by_origin,
            new_issues_by_origin=new_issues_by_origin,
            lab_maps={
                row[0]: LabMetricsData(
                    builds=row[1],
                    boots=row[2],
                    tests=row[3],
                )
                for row in lab_summary_results
            },
            prev_n_trees=prev_total_objects_result[0],
            prev_n_checkouts=prev_total_objects_result[1],
            prev_n_builds=prev_total_objects_result[2],
            prev_n_tests=prev_total_objects_result[3],
            prev_lab_maps={
                row[0]: LabMetricsData(
                    builds=row[1],
                    boots=row[2],
                    tests=row[3],
                )
                for row in prev_lab_summary_results
            },
        )
    except ValidationError as e:
        out(f"Validation error when constructing MetricsReportData: {e}")
        raise e

    return data


def warm_metrics_cache() -> None:
    today = datetime.now(timezone.utc).date()
    end_days_ago = (today - last_saturday(today)).days
    for period_days in METRICS_CACHE_WARM_PERIODS:
        out(
            f"Warming metrics cache for {period_days}-day Sat-Fri period "
            f"(end_days_ago={end_days_ago})"
        )
        try:
            get_metrics_data(
                start_days_ago=end_days_ago + period_days,
                end_days_ago=end_days_ago,
                use_cache=False,
                cache_timeout=METRICS_CACHE_WARM_TIMEOUT,
            )
            out(f"Warmed metrics cache for {period_days}-day period")
        except Exception as e:
            out(f"Failed to warm metrics cache for {period_days}-day period: {e}")
