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
            SELECT
                tests.id,
                tests.build_id,
                tests.status,
                tests.path,
                tests.log_excerpt,
                tests.log_url,
                tests.misc,
                tests.environment_misc,
                tests.start_time,
                builds.compiler,
                builds.architecture,
                builds.config_name,
                checkouts.git_commit_hash,
                checkouts.git_repository_branch,
                checkouts.git_repository_url
            FROM tests
            INNER JOIN builds
                ON tests.build_id = builds.id
            INNER JOIN checkouts
                ON builds.checkout_id = checkouts.id
            WHERE tests.id = %s
            """

        response = {}
        with connection.cursor() as cursor:
            cursor.execute(query, [test_id])
            rows = cursor.fetchall()
            if rows:
                for idx, key in enumerate(names_map.keys()):
                    response[key] = rows[0][idx]

        return JsonResponse(response, safe=False)
