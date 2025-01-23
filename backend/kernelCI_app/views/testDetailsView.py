from django.http import JsonResponse
from django.db import connection
from django.views import View
from http import HTTPStatus
from kernelCI_app.helpers.errorHandling import create_error_response
from kernelCI_app.utils import string_to_json


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
            "environment_compatible": "combined_tests.environment_compatible",
            "output_files": "combined_tests.output_files",
            "compiler": "builds.compiler",
            "architecture": "builds.architecture",
            "config_name": "builds.config_name",
            "git_commit_hash": "checkouts.git_commit_hash",
            "git_repository_branch": "checkouts.git_repository_branch",
            "git_repository_url": "checkouts.git_repository_url",
            "git_commit_tags": "checkouts.git_commit_tags",
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
                tests.environment_compatible,
                tests.output_files,
                builds.compiler,
                builds.architecture,
                builds.config_name,
                checkouts.git_commit_hash,
                checkouts.git_repository_branch,
                checkouts.git_repository_url,
                checkouts.git_commit_tags
            FROM tests
            LEFT JOIN builds
                ON tests.build_id = builds.id
            LEFT JOIN checkouts
                ON builds.checkout_id = checkouts.id
            WHERE tests.id = %s
            """

        response = {}
        with connection.cursor() as cursor:
            cursor.execute(query, [test_id])
            row = cursor.fetchone()
            if row:
                for idx, key in enumerate(names_map.keys()):
                    response[key] = row[idx]
                response["misc"] = string_to_json(response["misc"])
                response["environment_misc"] = string_to_json(response["environment_misc"])
                response["output_files"] = string_to_json(response["output_files"])

        if len(response) == 0:
            return create_error_response(
                error_message="Test not found", status_code=HTTPStatus.OK
            )

        return JsonResponse(response, safe=False)
