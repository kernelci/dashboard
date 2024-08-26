from django.http import JsonResponse
from django.views import View
from django.db import connection


class TestsByTreeAndCommitHash(View):
    def get(self, request, commit_hash: str | None):
        path_param = request.GET.get("path")
        origin_param = request.GET.get("origin")
        git_url_param = request.GET.get("git_url")
        git_branch_param = request.GET.get("git_branch")
        boot_param_with_wildcard = "boot.%"
        boot_param_exact = "boot"

        query = """
            SELECT t.id, c.git_repository_url,
                   c.git_commit_hash, t.id, t.build_id, t.start_time, t.duration,
                   t.status as status, t.path, b.architecture, b.config_name,
                   b.compiler, t.environment_misc,
                   t.environment_comment, t.misc
            FROM checkouts AS c
            INNER JOIN builds AS b ON c.id = b.checkout_id
            INNER JOIN tests AS t ON t.build_id = b.id
            WHERE c.git_commit_hash = %s
              AND c.origin = %s
              AND c.git_repository_url = %s
              AND c.git_repository_branch = %s
        """

        # Append the path filter conditionally
        if path_param == 'boot':
            query += " AND (t.path LIKE %s OR t.path = %s)"
            parameters = (
                commit_hash, origin_param, git_url_param, git_branch_param,
                boot_param_with_wildcard, boot_param_exact
            )
        else:
            query += " AND (t.path NOT LIKE %s AND t.path != %s)"
            parameters = (
                commit_hash, origin_param, git_url_param, git_branch_param,
                boot_param_with_wildcard, boot_param_exact
            )

        query += """
            ORDER BY
              t.path,
              CASE t.status
                  WHEN 'FAIL' THEN 1
                  WHEN 'ERROR' THEN 2
                  WHEN 'MISS' THEN 3
                  WHEN 'PASS' THEN 4
              ELSE 4
              END;
        """

        with connection.cursor() as cursor:
            cursor.execute(
                query,
                parameters
            )
            rows = cursor.fetchall()

        # Format the results as JSON
        results = [
            {
                "status": row[7],
                "path": row[8],
                "duration": row[6],
                "startTime": row[5],
            }
            for row in rows
        ]

        # TODO Validate output
        return JsonResponse(
            {
                "tests": results,
            }
        )
