#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
from django.db import connection

from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.queries.tree import get_tree_listing_query


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
                row_dict = dict(zip(col_names, row))
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
            fi.git_commit_name
    """

    return kcidb_execute_query(query, params)


def kcidb_build_incidents(issue_id):
    """Fetches build incidents of a given issue."""

    params = {"issue_id": issue_id}

    query = """
        SELECT DISTINCT ON (b.config_name, b.architecture, b.compiler)
            b.id,
            b.config_name,
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


# Similar to get_tree_listing_data, but at the same time it has to be different.
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
                            config_name
                        ORDER BY
                            start_time DESC NULLS LAST
                    ) AS rn,
                    FIRST_VALUE(git_commit_hash) OVER (
                        PARTITION BY
                            path,
                            platform,
                            config_name
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
            start_time DESC NULLS LAST;
        """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        # TODO: check if it is possible to remove dict_fetchall.
        # dict_fetchall has a performance impact and this query returns many rows,
        # so they shouldn't be together
        return dict_fetchall(cursor=cursor)
