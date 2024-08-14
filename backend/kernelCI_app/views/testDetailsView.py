from django.http import JsonResponse
from django.db import connection
from django.views import View


class TestDetails(View):
    def get(self, _request, test_id: str | None):
        names_map = {
            "id": "combined_tests.id",
            "build_id": "combined_tests.build_id",
            "status": "combined_tests.status",
            "path": "combined_tests.path",
            "log_excerpt": "combined_tests.log_excerpt",
            "log_url": "combined_tests.log_url",
            "misc": "combined_tests.misc",
            "environment_misc": "combined_tests.environment_misc",
            "start_time": "combined_tests.start_time",
            "compiler": "builds.compiler",
            "architecture": "builds.architecture",
            "config_name": "builds.config_name",
            "git_commit_hash": "checkouts.git_commit_hash",
            "git_repository_branch": "checkouts.git_repository_branch",
            "git_repository_url": "checkouts.git_repository_url",
        }

        query = """
            WITH current_test AS (
                SELECT *
                FROM tests
                WHERE id = %s
                LIMIT 1
            )
            SELECT
                combined_tests.id,
                combined_tests.build_id,
                combined_tests.status,
                combined_tests.path,
                combined_tests.log_excerpt,
                combined_tests.log_url,
                combined_tests.misc,
                combined_tests.environment_misc,
                combined_tests.start_time,
                builds.compiler,
                builds.architecture,
                builds.config_name,
                checkouts.git_commit_hash,
                checkouts.git_repository_branch,
                checkouts.git_repository_url
            FROM (
                SELECT
                    id,
                    build_id,
                    status,
                    path,
                    log_excerpt,
                    log_url,
                    misc,
                    environment_misc,
                    start_time
                FROM tests
                WHERE build_id = (SELECT build_id FROM current_test)
                -- A dot to get only descendants of this test
                  AND path LIKE (SELECT path FROM current_test) || '.%%'
                UNION
                SELECT
                    id,
                    build_id,
                    status,
                    path,
                    log_excerpt,
                    log_url,
                    misc,
                    environment_misc,
                    start_time
                FROM current_test
            ) AS combined_tests
            INNER JOIN builds
                ON combined_tests.build_id = builds.id
            INNER JOIN checkouts
                ON builds.checkout_id = checkouts.id
            ORDER BY
                (combined_tests.id = %s) DESC,
                combined_tests.id;
            """

        response_data = []
        with connection.cursor() as cursor:
            cursor.execute(query, [test_id, test_id])
            rows = cursor.fetchall()

            for row in rows:
                item = {}
                for idx, key in enumerate(names_map.keys()):
                    item[key] = row[idx]
                response_data.append(item)
        return JsonResponse({"tests": response_data}, safe=False)
