from typing import Optional
from django.db import connection
from kernelCI_app.cache import get_query_cache, set_query_cache
from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.models import Checkouts, Issues


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
            T.ID,
            T.STATUS,
            T.DURATION,
            T.PATH,
            T.START_TIME,
            T.ENVIRONMENT_COMPATIBLE,
            T.ENVIRONMENT_MISC,
            C.TREE_NAME,
            C.GIT_REPOSITORY_BRANCH,
            C.GIT_REPOSITORY_URL
        FROM
            INCIDENTS INC
            INNER JOIN TESTS T ON (INC.TEST_ID = T.ID)
            LEFT JOIN BUILDS B ON (T.BUILD_ID = B.ID)
            LEFT JOIN CHECKOUTS C ON (B.CHECKOUT_ID = C.ID)
        WHERE
            (
                INC.ISSUE_ID = %(issue_id)s
                AND {version_clause}
            )
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return dict_fetchall(cursor)


def get_issue_listing_data(
    *,
    interval: str,
) -> list[dict]:
    """Queries the list of all issues from `interval_date` parameter to now.

    Returns the list of issue records (dict) with no other filter."""

    params = {"interval": interval}

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
        i._timestamp >= NOW() - INTERVAL %(interval)s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return dict_fetchall(cursor)


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


def get_issue_first_seen_data(*, issue_id_list: list[str]) -> list[dict]:
    """Retrieves the incident and checkout data
    of the first incident of a list of issues
    through a list of `issue_id`s."""

    if not issue_id_list:
        return []

    cache_key = "issue_first_seen"
    params = {"issue_id_list": issue_id_list}
    records = get_query_cache(key=cache_key, params=params)

    if records is None:
        placeholders = ", ".join(["%s"] * len(issue_id_list))

        # TODO: use '=' instead of 'IN' when the list has a single element
        query = f"""
            WITH first_incident AS (
                SELECT DISTINCT
                    ON (IC.issue_id) IC.id
                FROM
                    incidents IC
                WHERE
                    IC.issue_id IN ({placeholders})
                ORDER BY
                    IC.issue_id,
                    IC.issue_version ASC,
                    IC._timestamp ASC
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
                C.tree_name
            FROM
                incidents IC
            LEFT JOIN tests T ON IC.test_id = T.id
            LEFT JOIN builds B ON (
                IC.build_id = B.id
                OR T.build_id = B.id
            )
            LEFT JOIN checkouts C ON B.checkout_id = C.id
            JOIN first_incident FI ON IC.id = FI.id
        """

        with connection.cursor() as cursor:
            cursor.execute(query, issue_id_list)
            records = dict_fetchall(cursor)

        set_query_cache(key=cache_key, params=params, rows=records)

    return records


def get_issue_trees_data(*, issue_key_list: list[tuple[str, int]]):
    """Retrieves the list of trees in which a list of issues appear
    through a list of tuples `issue_id, issue_version`.\n
    The return is a single list where each element contains
    the checkout data and the issue_id and issue_version of the incident."""

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

    # TODO: use '=' instead of 'IN' when the list has a single element
    records = Checkouts.objects.raw(
        f"""
        SELECT DISTINCT
            ON (
                C.TREE_NAME,
                C.GIT_REPOSITORY_URL,
                C.GIT_REPOSITORY_BRANCH,
                IC.ISSUE_ID,
                IC.ISSUE_VERSION
            )
            C.ID,
            C.TREE_NAME,
            C.GIT_REPOSITORY_URL,
            C.GIT_REPOSITORY_BRANCH,
            IC.ISSUE_ID,
            IC.ISSUE_VERSION
        FROM
            INCIDENTS IC
            LEFT JOIN TESTS T ON IC.TEST_ID = T.ID
            LEFT JOIN BUILDS B ON (
                IC.BUILD_ID = B.ID
                OR T.BUILD_ID = B.ID
            )
            JOIN CHECKOUTS C ON B.CHECKOUT_ID = C.ID
        WHERE
            (IC.ISSUE_ID, IC.ISSUE_VERSION) IN ({tuple_str})
        """,
        params,
    )

    return records
