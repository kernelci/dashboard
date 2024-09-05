from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.db import connection


# TODO Move this endpoint to a function so it doesn't
# have to be another request, it can be called from the tree details endpoint
class TreeCommitsHistory(APIView):
    def get(self, request, commit_hash):
        origin_param = request.GET.get("origin")
        git_url_param = request.GET.get("git_url")
        git_branch_param = request.GET.get("git_branch")

        missing_params = []
        if not origin_param:
            missing_params.append("origin")
        if not git_url_param:
            missing_params.append("git_url")
        if not git_branch_param:
            missing_params.append("git_branch")

        if missing_params:
            return Response(
                {"error": f"Missing parameters: {', '.join(missing_params)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query = """
        WITH
        relevant_checkouts AS (
            SELECT
                id,
                git_commit_hash,
                git_commit_name,
                git_repository_branch,
                git_repository_url,
                origin,
                start_time
            FROM
                checkouts
            WHERE
                git_repository_branch = %(git_branch_param)s
                AND git_repository_url = %(git_url_param)s
                AND origin = %(origin_param)s
            ORDER BY
                start_time DESC
        ),
        earliest_commits AS (
            SELECT
                git_commit_hash,
                git_commit_name,
                MAX(start_time) AS earliest_start_time
            FROM
                relevant_checkouts
            GROUP BY
                git_commit_hash,
                git_commit_name
            ORDER BY
                earliest_start_time DESC
            LIMIT 6
        ),
        build_counts AS (
            SELECT
                c.git_commit_hash,
                SUM(CASE WHEN b.valid = true THEN 1 ELSE 0 END) AS valid_builds,
                SUM(CASE WHEN b.valid = false THEN 1 ELSE 0 END) AS invalid_builds,
                SUM(CASE WHEN b.valid IS NULL THEN 1 ELSE 0 END) AS null_builds
            FROM
                relevant_checkouts AS c
            INNER JOIN
                builds AS b
                ON c.id = b.checkout_id
            WHERE
                c.git_repository_branch = %(git_branch_param)s
                AND c.git_repository_url = %(git_url_param)s
                AND c.origin = %(origin_param)s
            GROUP BY
                c.git_commit_hash
        ),
        test_counts AS (
        SELECT
            c.git_commit_hash,
            SUM(CASE WHEN t.status = 'FAIL' AND t.path LIKE 'boot%%' THEN 1 ELSE 0 END) AS boots_fail_count,
            SUM(CASE WHEN t.status = 'ERROR' AND t.path LIKE 'boot%%' THEN 1 ELSE 0 END) AS boots_error_count,
            SUM(CASE WHEN t.status = 'MISS' AND t.path LIKE 'boot%%' THEN 1 ELSE 0 END) AS boots_miss_count,
            SUM(CASE WHEN t.status = 'PASS' AND t.path LIKE 'boot%%' THEN 1 ELSE 0 END) AS boots_pass_count,
            SUM(CASE WHEN t.status = 'DONE' AND t.path LIKE 'boot%%' THEN 1 ELSE 0 END) AS boots_done_count,
            SUM(CASE WHEN t.status = 'SKIP' AND t.path LIKE 'boot%%' THEN 1 ELSE 0 END) AS boots_skip_count,
            SUM(CASE WHEN t.status = 'FAIL' AND t.path NOT LIKE 'boot%%' THEN 1 ELSE 0 END)
            AS non_boots_fail_count,
            SUM(CASE WHEN t.status = 'ERROR' AND t.path NOT LIKE 'boot%%' THEN 1 ELSE 0 END)
            AS non_boots_error_count,
            SUM(CASE WHEN t.status = 'MISS' AND t.path NOT LIKE 'boot%%' THEN 1 ELSE 0 END)
            AS non_boots_miss_count,
            SUM(CASE WHEN t.status = 'PASS' AND t.path NOT LIKE 'boot%%' THEN 1 ELSE 0 END)
            AS non_boots_pass_count,
            SUM(CASE WHEN t.status = 'DONE' AND t.path NOT LIKE 'boot%%' THEN 1 ELSE 0 END)
            AS non_boots_done_count,
            SUM(CASE WHEN t.status = 'SKIP' AND t.path NOT LIKE 'boot%%' THEN 1 ELSE 0 END)
            AS non_boots_skip_count
        FROM
            relevant_checkouts AS c
        INNER JOIN
            builds AS b
            ON
            c.id = b.checkout_id
        LEFT JOIN
            tests AS t
            ON b.id = t.build_id
        WHERE
            b.start_time >= (
                SELECT
                    MIN(earliest_start_time)
                FROM earliest_commits
            )
            AND t.start_time >= (
                SELECT
                    MIN(earliest_start_time)
                FROM earliest_commits
            )
        GROUP BY
            c.git_commit_hash
        )
        SELECT
            ec.git_commit_hash,
            ec.git_commit_name,
            ec.earliest_start_time,
            bc.valid_builds,
            bc.invalid_builds,
            bc.null_builds,
            tc.boots_fail_count,
            tc.boots_error_count,
            tc.boots_miss_count,
            tc.boots_pass_count,
            tc.boots_done_count,
            tc.boots_skip_count,
            tc.non_boots_fail_count,
            tc.non_boots_error_count,
            tc.non_boots_miss_count,
            tc.non_boots_pass_count,
            tc.non_boots_done_count,
            tc.non_boots_skip_count
        FROM
            earliest_commits AS ec
        INNER JOIN
            build_counts AS bc
            ON ec.git_commit_hash = bc.git_commit_hash
        INNER JOIN
            test_counts AS tc
            ON ec.git_commit_hash = tc.git_commit_hash
        ORDER BY
            ec.earliest_start_time DESC
        LIMIT 6;
        """

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                {
                    "commit_hash": commit_hash,
                    "origin_param": origin_param,
                    "git_url_param": git_url_param,
                    "git_branch_param": git_branch_param,
                },
            )
            rows = cursor.fetchall()

        # Format the results as JSON
        results = [
            {
                "git_commit_hash": row[0],
                "git_commit_name": row[1],
                "earliest_start_time": row[2],
                "builds": {
                    "valid_builds": row[3],
                    "invalid_builds": row[4],
                    "null_builds": row[5],
                },
                "boots_tests": {
                    "fail_count": row[6],
                    "error_count": row[7],
                    "miss_count": row[8],
                    "pass_count": row[9],
                    "done_count": row[10],
                    "skip_count": row[11],
                },
                "non_boots_tests": {
                    "fail_count": row[12],
                    "error_count": row[13],
                    "miss_count": row[14],
                    "pass_count": row[15],
                    "done_count": row[16],
                    "skip_count": row[17],
                },
            }
            for row in rows
        ]

        return JsonResponse(results, safe=False)
