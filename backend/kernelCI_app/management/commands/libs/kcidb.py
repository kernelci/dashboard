#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import psycopg2


def kcidb_execute_query(conn, query, params=None):
    try:
        with conn.cursor() as cur:
            # print(cur.mogrify(query, params).decode('utf-8'))
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
    except psycopg2.Error as e:
        print(f"Query execution failed: {e}")
        sys.exit()


def kcidb_new_issues(conn, origin):
    """Fetch issues from the last few days, including related checkouts."""

    params = {"origin": origin, "interval": "4 days"}

    query = """
        WITH ranked_issues AS (
        SELECT
            i._timestamp,
            i.id,
            i.version,
            i.comment,
            i.misc,
            ROW_NUMBER() OVER (PARTITION BY i.id ORDER BY i.version DESC) AS rn
        FROM
            public.issues i
        WHERE origin = %(origin)s
            AND i._timestamp >= NOW() - INTERVAL '4 days'
        ),

        highest_version AS (
        SELECT
            _timestamp,
            id,
            version,
            comment,
            misc
        FROM
            ranked_issues
        WHERE
            rn = 1 -- Keep only the highest version for each id
        ),

        older_issues AS (
        SELECT h._timestamp, h.id, h.version, h.comment, h.misc
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
           WHERE inc.origin = %(origin)s
            AND inc._timestamp >= NOW() - INTERVAL %(interval)s

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
           WHERE inc.origin = %(origin)s
            AND inc._timestamp >= NOW() - INTERVAL %(interval)s
            AND (t.path = 'boot' OR t.path = 'boot.nfs')
       )

        SELECT
            fi._timestamp,
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
        FROM new_issues n
        LEFT JOIN first_incidents fi ON n.id = fi.issue_id AND fi.incident_rn = 1
        LEFT JOIN incidents inc ON n.id = inc.issue_id
        GROUP BY  -- Important: Group by all selected columns *except* the count
            fi._timestamp,
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
        ORDER BY fi._timestamp DESC;
        """

    return kcidb_execute_query(conn, query, params)


def kcidb_issue_details(conn, issue_id):
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

    return kcidb_execute_query(conn, query, params)


def kcidb_build_incidents(conn, issue_id):
    """Fetches build incidents of a given issue."""

    params = {"issue_id": issue_id}

    query = """
        SELECT DISTINCT ON (b.config_name, b.architecture, b.compiler)
            b.*
        FROM builds b
            LEFT JOIN incidents inc ON inc.build_id = b.id
        WHERE inc.issue_id = %(issue_id)s
        ORDER BY b.config_name, b.architecture, b.compiler, b._timestamp DESC;
    """

    return kcidb_execute_query(conn, query, params)


def kcidb_test_incidents(conn, issue_id):
    """Fetches test incidents of a given issue."""

    params = {"issue_id": issue_id}

    query = """
        WITH ranked_tests AS (
            SELECT
                t.*,
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

    return kcidb_execute_query(conn, query, params)


def kcidb_last_test_without_issue(conn, issue, incident):
    """Fetches build incidents of a given issue."""

    params = {
        "origin": "maestro",
        "issue_id": issue["id"],
        "path": incident["path"],
        "platform": incident["platform"],
        "timestamp": incident["oldest_timestamp"],
        "giturl": issue["git_repository_url"],
        "branch": issue["git_repository_branch"],
    }

    query = """
    WITH ranked_tests AS (
        SELECT
            t.*,
            c.git_repository_url,
            c.tree_name,
            c.git_repository_branch,
            c.git_commit_hash,
            ROW_NUMBER() OVER
                (PARTITION BY t.environment_misc->>'platform', t.path ORDER BY t._timestamp DESC) as rn
        FROM tests t
        LEFT JOIN builds b ON b.id = t.build_id
        LEFT JOIN checkouts c ON c.id = b.checkout_id
        WHERE t.origin = %(origin)s
            AND t._timestamp < %(timestamp)s
            AND t.environment_misc->>'platform' = %(platform)s
            AND t.path = %(path)s
            AND t.status = 'PASS'
            AND c.git_repository_url = %(giturl)s
            AND c.git_repository_branch = %(branch)s
        LIMIT 10
    )

        SELECT *
            FROM ranked_tests
            WHERE rn = 1
    """

    return kcidb_execute_query(conn, query, params)


def kcidb_last_test_without_issue_koike(conn, issue, incident):
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

    return kcidb_execute_query(conn, query, params)


def kcidb_latest_checkout_results(conn, origin, giturl, branch):
    """
    Fetches checkouts between in the past 5 to 29 hours.
    As KCIDB doesn't have an end of testing signal, we have
    to wait sometime before we can send the report.
    """

    params = {
        "origin": origin,
        "giturl": giturl,
        "branch": branch,
        "interval_min": "5 hours",
        "interval_max": "29 hours",
    }

    query = """
            SELECT *
                FROM checkouts c
                WHERE c.origin = %(origin)s
                AND c.git_repository_url = %(giturl)s
                AND c.git_repository_branch = %(branch)s
                AND c._timestamp >= NOW() - INTERVAL %(interval_max)s
                AND c._timestamp <= NOW() - INTERVAL %(interval_min)s
                ORDER BY c._timestamp DESC
                LIMIT 1
        """
    result = kcidb_execute_query(conn, query, params)
    return result[0] if result else None


def kcidb_tests_results(conn, origin, giturl, branch, hash, path):
    """Fetches build incidents of a given issue."""

    params = {
        "origin": origin,
        "giturl": giturl,
        "branch": branch,
        "hash": hash,
        "path": path,
        "interval": "25 days",
    }

    query = """
            WITH latest_checkout AS (
                SELECT
                    _timestamp
                FROM checkouts
                WHERE git_commit_hash = %(hash)s
            ),
            ranked_tests AS (
                SELECT
                    t.id,
                    t.path,
                    t.status,
                    t.start_time,
                    t.environment_misc->>'platform' AS platform,
                    b.architecture,
                    b.compiler,
                    b.config_name,
                    c.git_commit_hash,
                    ROW_NUMBER() OVER (
                        PARTITION BY t.path
                        ORDER BY t.start_time DESC NULLS LAST
                    ) as rn
                FROM tests t
                JOIN builds b ON t.build_id = b.id
                JOIN checkouts c ON b.checkout_id = c.id
                JOIN latest_checkout lc on lc._timestamp > c._timestamp
                WHERE t.origin = %(origin)s
                    AND c.git_repository_url = %(giturl)s
                    AND c.git_repository_branch = %(branch)s
                    AND t.path LIKE %(path)s
                    AND t.environment_misc->>'platform' != 'kubernetes'
                    AND c._timestamp >= NOW() - INTERVAL %(interval)s
                    AND b._timestamp >= NOW() - INTERVAL %(interval)s
                    AND t._timestamp >= NOW() - INTERVAL %(interval)s
            )
            SELECT *
            FROM ranked_tests
            WHERE rn <= 9
            ORDER BY path, start_time DESC NULLS LAST;
        """

    return kcidb_execute_query(conn, query, params)


def kcidb_connect():
    """Connect to PostgreSQL using the .pg_service.conf configuration."""
    try:
        conn = psycopg2.connect(
            "service=kcidb-local-proxy"
        )  # Uses the configuration from ~/.pg_service.conf
        return conn
    except psycopg2.Error as e:
        print(f"Database connection failed: {e}")
        return None
