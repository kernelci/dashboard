from datetime import datetime
from typing import Any, Literal, Optional

from django.db import connection, connections

from kernelCI_app.cache import get_query_cache, set_query_cache
from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.models import Issues


def _get_issue_version_clause(*, version: Optional[int]) -> str:
    if version is None:
        version_clause = """
            INC.ISSUE_VERSION = (
                SELECT MAX(ISSUE_VERSION)
                FROM INCIDENTS
                WHERE ISSUE_ID = %(issue_id)s
            )"""
    else:
        version_clause = """
            INC.ISSUE_VERSION = %(issue_version)s
        """
    return version_clause


def get_issue_builds(*, issue_id: str, version: Optional[int]) -> list[dict]:
    version_clause = _get_issue_version_clause(version=version)

    params = {
        "issue_id": issue_id,
        "issue_version": version,
    }

    query = f"""
        SELECT
            B.ID,
            B.ARCHITECTURE,
            B.CONFIG_NAME,
            B.STATUS AS build_status,
            B.START_TIME,
            B.DURATION,
            B.COMPILER,
            B.LOG_URL,
            B.MISC,
            C.TREE_NAME,
            C.GIT_REPOSITORY_BRANCH,
            C.GIT_REPOSITORY_URL
        FROM
            INCIDENTS INC
            INNER JOIN BUILDS B ON (INC.BUILD_ID = B.ID)
            LEFT JOIN CHECKOUTS C ON (B.CHECKOUT_ID = C.ID)
        WHERE
            INC.ISSUE_ID = %(issue_id)s
            AND {version_clause}
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return dict_fetchall(cursor)


def get_issue_tests(*, issue_id: str, version: Optional[int]) -> list[dict]:
    version_clause = _get_issue_version_clause(version=version)

    params = {
        "issue_id": issue_id,
        "issue_version": version,
    }

    query = f"""
        SELECT
            INC.TEST_ID AS ID,
            T.STATUS,
            T.DURATION,
            T.PATH,
            T.START_TIME,
            T.ENVIRONMENT_COMPATIBLE,
            T.ENVIRONMENT_MISC,
            -- TODO remove MISC->>'runtime' fallback after lab backfill
            COALESCE(TL.NAME, T.MISC->>'runtime') AS lab,
            C.TREE_NAME,
            C.GIT_REPOSITORY_BRANCH,
            C.GIT_REPOSITORY_URL
        FROM
            INCIDENTS INC
            LEFT JOIN TESTS T ON (INC.TEST_ID = T.ID)
            LEFT JOIN LABS TL ON (T.LAB_ID = TL.ID)
            LEFT JOIN BUILDS B ON (T.BUILD_ID = B.ID)
            LEFT JOIN CHECKOUTS C ON (B.CHECKOUT_ID = C.ID)
        WHERE
            (
                INC.ISSUE_ID = %(issue_id)s
                AND {version_clause}
            )
            AND INC.TEST_ID IS NOT NULL
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return dict_fetchall(cursor)


def get_issue_listing_data(
    *,
    start_date: datetime,
    end_date: datetime,
) -> list[dict]:
    """Queries the list of all issues whose timestamp falls within [start_date, end_date].

    Returns the list of issue records (dict) with no other filter."""

    params = {
        "start_date": start_date,
        "end_date": end_date,
    }
    cache_params = {
        "start_date": int(start_date.timestamp()),
        "end_date": int(end_date.timestamp()),
    }
    cache_key = "issueList"

    rows = get_query_cache(key=cache_key, params=cache_params)
    if rows is not None:
        return rows

    # Note that an issue with timestamp younger than x days ago
    # can still have incidents in tests older than x days ago
    query = """
    SELECT
        i.id,
        i._timestamp AS field_timestamp,
        i.comment,
        i.version,
        i.origin,
        i.culprit_code,
        i.culprit_harness,
        i.culprit_tool,
        i.categories,
        EXISTS (
            SELECT 1
            FROM incidents inc
            WHERE i.id = inc.issue_id
        ) AS has_incident
    FROM
        issues i
    WHERE
        i._timestamp >= %(start_date)s
        AND i._timestamp <= %(end_date)s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = dict_fetchall(cursor)
        set_query_cache(key=cache_key, params=cache_params, rows=rows)
        return rows


# TODO: combine this query with the other queries for issues
def get_latest_issue_version(*, issue_id: str) -> Optional[dict]:
    version_row = (
        Issues.objects.values("version")
        .filter(id=issue_id)
        .order_by("-version")
        .first()
    )
    return version_row


def get_issue_details(*, issue_id: str, version: int) -> Optional[dict]:
    query = (
        Issues.objects.values(
            "field_timestamp",
            "id",
            "version",
            "origin",
            "report_url",
            "report_subject",
            "culprit_code",
            "culprit_tool",
            "culprit_harness",
            "comment",
            "misc",
            "categories",
        )
        .filter(id=issue_id, version=version)
        .first()
    )

    return query


def get_build_issues(*, build_id: str) -> list[dict]:
    """Retrieves the issues of a given build through a build_id"""

    query = """
        SELECT
            incidents.id,
            issues.id,
            issues.version,
            issues.comment,
            issues.report_url,
            builds.status AS status
        FROM incidents
        JOIN issues
            ON incidents.issue_id = issues.id
            AND incidents.issue_version = issues.version
        JOIN builds
            ON incidents.build_id = builds.id
        WHERE incidents.build_id = %s
        """
    with connection.cursor() as cursor:
        cursor.execute(query, [build_id])
        rows = dict_fetchall(cursor=cursor)

    return rows


def get_test_issues(*, test_id: str) -> list[dict]:
    """Retrieves the issues of a given test through a test_id"""

    query = """
        SELECT
            incidents.id,
            issues.id,
            issues.version,
            issues.comment,
            issues.report_url,
            tests.status AS status
        FROM incidents
        JOIN issues
            ON incidents.issue_id = issues.id
            AND incidents.issue_version = issues.version
        JOIN tests
            ON incidents.test_id = tests.id
        WHERE incidents.test_id = %s
        """
    with connection.cursor() as cursor:
        cursor.execute(query, [test_id])
        rows = dict_fetchall(cursor=cursor)

    return rows


def get_issue_seen_data(
    *,
    issue_id_list: list[str],
    mode: Literal["first", "last"] = "first",
    group_by: Literal["issue", "tree"] = "issue",
) -> list[dict]:
    """
    Retrieves the incident and checkout data of either the first or last
    incident of a list of issues through a list of `issue_id`s.

    :param mode: Either 'first' to get oldest incidents or 'last' to get the newest ones.
    :param group_by: 'issue' returns one row per issue; 'tree' returns one row per
        (issue, tree_name, git_repository_url, git_repository_branch).
    """
    if not issue_id_list:
        return []

    order_direction = "ASC" if mode == "first" else "DESC"
    cache_key = f"issue_{mode}_seen"
    if group_by == "tree":
        cache_key = f"{cache_key}_per_tree"
    params = {"issue_id_list": issue_id_list}
    records = get_query_cache(key=cache_key, params=params)

    if records is None:
        if group_by == "tree":
            query = f"""
                SELECT DISTINCT ON (
                    IC.issue_id,
                    C.tree_name,
                    C.git_repository_url,
                    C.git_repository_branch
                )
                    IC.id,
                    IC.issue_id,
                    IC._timestamp AS first_seen,
                    IC.issue_version,
                    C.git_commit_hash,
                    C.git_repository_url,
                    C.git_repository_branch,
                    C.git_commit_name,
                    C.tree_name,
                    C.id AS checkout_id,
                    C.start_time AS checkout_start_time
                FROM
                    incidents IC
                LEFT JOIN tests T ON IC.test_id = T.id
                LEFT JOIN builds B ON (
                    IC.build_id = B.id
                    OR T.build_id = B.id
                )
                LEFT JOIN checkouts C ON B.checkout_id = C.id
                WHERE
                    IC.issue_id = ANY(%(issue_id_list)s)
                    AND C.tree_name IS NOT NULL
                    AND C.git_repository_branch IS NOT NULL
                ORDER BY
                    IC.issue_id,
                    C.tree_name,
                    C.git_repository_url,
                    C.git_repository_branch,
                    IC.issue_version {order_direction},
                    IC._timestamp {order_direction}
            """
        else:
            query = f"""
                WITH target_incident AS (
                    SELECT DISTINCT ON (IC.issue_id)
                        IC.id
                    FROM
                        incidents IC
                    WHERE
                        IC.issue_id = ANY(%(issue_id_list)s)
                    ORDER BY
                        IC.issue_id,
                        IC.issue_version {order_direction},
                        IC._timestamp {order_direction}
                )
                SELECT
                    IC.id,
                    IC.issue_id,
                    IC._timestamp AS first_seen,
                    IC.issue_version,
                    C.git_commit_hash,
                    C.git_repository_url,
                    C.git_repository_branch,
                    C.git_commit_name,
                    C.tree_name,
                    C.id as checkout_id
                FROM
                    incidents IC
                LEFT JOIN tests T ON IC.test_id = T.id
                LEFT JOIN builds B ON (
                    IC.build_id = B.id
                    OR T.build_id = B.id
                )
                LEFT JOIN checkouts C ON B.checkout_id = C.id
                JOIN target_incident TI ON IC.id = TI.id
            """

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            records = dict_fetchall(cursor)

        set_query_cache(key=cache_key, params=params, rows=records)

    return records


def get_issue_first_seen_data(
    *,
    issue_id_list: list[str],
    group_by: Literal["issue", "tree"] = "issue",
) -> list[dict]:
    """
    Retrieves the incident and checkout data
    of the first incident of a list of issues
    through a list of `issue_id`s.
    """
    return get_issue_seen_data(
        issue_id_list=issue_id_list, mode="first", group_by=group_by
    )


def get_issue_last_seen_data(
    *,
    issue_id_list: list[str],
    group_by: Literal["issue", "tree"] = "issue",
) -> list[dict]:
    """
    Retrieves the incident and checkout data
    of the last incident of a list of issues
    through a list of `issue_id`s.
    """
    return get_issue_seen_data(
        issue_id_list=issue_id_list, mode="last", group_by=group_by
    )


def get_issue_first_good_checkouts(
    *,
    last_seen_trees: list[dict],
) -> list[dict]:
    """
    For each (issue_id, tree, url, branch, last_seen) entry, returns the earliest
    checkout on that tree with start_time > last_seen and no incident for the issue.

    Uses a single query with a LATERAL join so PostgreSQL does one indexed lookup
    per tree instead of scanning every later checkout for every tree.

    :param last_seen_trees: dicts with keys issue_id, tree_name, git_repository_url,
        git_repository_branch, last_seen (datetime).
    """
    if not last_seen_trees:
        return []

    params = {
        "issue_ids": [entry["issue_id"] for entry in last_seen_trees],
        "tree_names": [entry["tree_name"] for entry in last_seen_trees],
        "git_repository_urls": [
            entry["git_repository_url"] for entry in last_seen_trees
        ],
        "git_repository_branches": [
            entry["git_repository_branch"] for entry in last_seen_trees
        ],
        "last_seens": [entry["last_seen"] for entry in last_seen_trees],
    }

    query = """
        WITH last_seen_trees AS (
            SELECT *
            FROM unnest(
                %(issue_ids)s::text[],
                %(tree_names)s::text[],
                %(git_repository_urls)s::text[],
                %(git_repository_branches)s::text[],
                %(last_seens)s::timestamptz[]
            ) AS t(
                issue_id,
                tree_name,
                git_repository_url,
                git_repository_branch,
                last_seen
            )
        )
        SELECT
            ls.issue_id,
            good.checkout_id,
            good.start_time,
            good.git_commit_hash,
            good.git_repository_url,
            good.git_repository_branch,
            good.git_commit_name,
            good.tree_name
        FROM
            last_seen_trees ls
            CROSS JOIN LATERAL (
                SELECT
                    C.id AS checkout_id,
                    C.start_time,
                    C.git_commit_hash,
                    C.git_repository_url,
                    C.git_repository_branch,
                    C.git_commit_name,
                    C.tree_name
                FROM checkouts C
                WHERE
                    C.tree_name = ls.tree_name
                    AND C.git_repository_url IS NOT DISTINCT FROM ls.git_repository_url
                    AND C.git_repository_branch = ls.git_repository_branch
                    AND C.start_time > ls.last_seen
                    AND NOT EXISTS (
                        SELECT 1
                        FROM incidents IC
                        LEFT JOIN tests T ON IC.test_id = T.id
                        LEFT JOIN builds B ON (
                            IC.build_id = B.id
                            OR T.build_id = B.id
                        )
                        WHERE
                            IC.issue_id = ls.issue_id
                            AND B.checkout_id = C.id
                    )
                ORDER BY C.start_time ASC
                LIMIT 1
            ) good
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return dict_fetchall(cursor)


def get_issue_trees_data(
    *, issue_key_list: list[tuple[str, int]]
) -> list[dict[str, Any]]:
    """
    Retrieves the list of trees in which a list of issues appears
    through a list of tuples `issue_id, issue_version`.

    If an `(issue_id, issue_version)` doesn't exist,
    the entry for that won't be returned.

    However, if an (issue_id, issue_version) exists but has no incidents,
    a row with the issue_id will be returned but the incident_issue_id will be null

    Returns:
        - A list of entries with the issue_id, issue_version, checkout data,
          and incident_issue_id and incident_issue_version
    """

    if not issue_key_list:
        return []

    tuple_param_list = []
    params = {}

    for index, key in enumerate(issue_key_list):
        id_key = f"id{index}"
        version_key = f"version{index}"

        tuple_string = f"(%({id_key})s, %({version_key})s)"

        tuple_param_list.append(tuple_string)
        params[id_key] = key[0]
        params[version_key] = key[1]
    tuple_str = ", ".join(tuple_param_list)

    if len(tuple_param_list) == 1:
        comparison = "="
    else:
        comparison = "IN"

    # The query starts from the issues table in order to differentiate
    # between "issue doesn't exist" and "issue has no incidents"
    query = f"""
        SELECT DISTINCT
            ON (
                C.TREE_NAME,
                C.GIT_REPOSITORY_URL,
                C.GIT_REPOSITORY_BRANCH,
                I.ID,
                I.VERSION
            )
            I.ID AS ISSUE_ID,
            I.VERSION AS ISSUE_VERSION,
            C.ID AS CHECKOUT_ID,
            C.TREE_NAME,
            C.GIT_REPOSITORY_URL,
            C.GIT_REPOSITORY_BRANCH,
            IC.ISSUE_ID AS INCIDENT_ISSUE_ID,
            IC.ISSUE_VERSION AS INCIDENT_ISSUE_VERSION
        FROM
            ISSUES I
            LEFT JOIN INCIDENTS IC ON (IC.ISSUE_ID, IC.ISSUE_VERSION) = (I.ID, I.VERSION)
            LEFT JOIN TESTS T ON IC.TEST_ID = T.ID
            LEFT JOIN BUILDS B ON (
                IC.BUILD_ID = B.ID
                OR T.BUILD_ID = B.ID
            )
            LEFT JOIN CHECKOUTS C ON B.CHECKOUT_ID = C.ID
        WHERE
            (I.ID, I.VERSION) {comparison} ({tuple_str})
        """

    with connections["default"].cursor() as cursor:
        cursor.execute(query, params)
        records = dict_fetchall(cursor)

    return records
