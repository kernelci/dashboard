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
        WITH earliest_commits AS (
            SELECT
                git_commit_hash,
                MIN(start_time) AS earliest_start_time
            FROM
                checkouts
            WHERE
                git_repository_branch = %(git_branch_param)s
                AND git_repository_url = %(git_url_param)s
                AND origin = %(origin_param)s
            GROUP BY
                git_commit_hash
        ),
        build_counts AS (
            SELECT
                c.git_commit_hash,
                SUM(CASE WHEN b.valid = true THEN 1 ELSE 0 END) AS valid_builds,
                SUM(CASE WHEN b.valid = false THEN 1 ELSE 0 END) AS invalid_builds,
                SUM(CASE WHEN b.valid IS NULL THEN 1 ELSE 0 END) AS null_builds
            FROM
                checkouts AS c
            INNER JOIN
                builds AS b
                ON c.id = b.checkout_id
            WHERE
                c.git_repository_branch = %(git_branch_param)s
                AND c.git_repository_url = %(git_url_param)s
                AND c.origin = %(origin_param)s
            GROUP BY
                c.git_commit_hash
        )
        SELECT
            ec.git_commit_hash,
            ec.earliest_start_time,
            bc.valid_builds,
            bc.invalid_builds,
            bc.null_builds
        FROM
            earliest_commits AS ec
        INNER JOIN
            build_counts AS bc
            ON ec.git_commit_hash = bc.git_commit_hash
        WHERE
            ec.earliest_start_time <= (
                SELECT
                    earliest_start_time
                FROM
                    earliest_commits
                WHERE
                    git_commit_hash = %(commit_hash)s
            )
        ORDER BY
            ec.earliest_start_time DESC
        LIMIT 5;
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
                "earliest_start_time": row[1],
                "valid_builds": row[2],
                "invalid_builds": row[3],
                "null_builds": row[4],
            }
            for row in rows
        ]

        return JsonResponse(results, safe=False)
