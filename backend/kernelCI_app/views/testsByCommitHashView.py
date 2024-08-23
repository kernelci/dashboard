from django.http import JsonResponse
from django.views import View
from kernelCI_app.models import Tests


class TestsByCommitHash(View):
    def get(self, request, commit_hash: str | None):
        path_param = request.GET.get("path")
        path_param = "boot"
        if path_param:
            path_filter = "AND t.path NOT LIKE %s"
            params = [commit_hash, f"{path_param}%"]
        else:
            path_filter = ""
            params = [commit_hash]

        names_map = {
            "t.id": "id",
            "c.git_repository_url": "git_repository_url",
            "c.git_commit_hash": "git_commit_hash",
            "t.build_id": "build_id",
            "t.start_time": "start_time",
            "t.status": "status",
            "t.path": "path",
            "b.architecture": "architecture",
            "b.config_name": "config_name",
            "b.compiler": "compiler",
            "t.environment_misc": "environment_misc",
            "t.environment_comment": "environment_comment",
            "t.misc": "misc",
        }

        # TODO: Remove the f string here and use parametrized queries
        query = Tests.objects.raw(
            f"""
                SELECT t.id, c.git_repository_url,
                c.git_commit_hash, t.id, t.build_id, t.start_time,
                t.status as status, t.path, b.architecture, b.config_name,
                b.compiler, t.environment_misc,
                t.environment_comment, t.misc FROM checkouts AS c
                INNER JOIN builds AS b ON c.id = b.checkout_id
                INNER JOIN tests AS t ON t.build_id = b.id
                WHERE c.git_commit_hash = %s {path_filter}
                ORDER BY
                build_id,
                CASE t.status
                    WHEN 'FAIL' THEN 1
                    WHEN 'ERROR' THEN 2
                    WHEN 'MISS' THEN 3
                    WHEN 'PASS' THEN 4
                ELSE 4
                END;
            """,
            params,
            translations=names_map,
        )

        tests = []
        for record in query:
            print(record)
            tests.append(
                {
                    "id": record.id,
                    "architecture": record.architecture,
                    "compiler": record.compiler,
                    "status": record.status,
                    "path": record.path,
                }
            )

        # TODO Validate output
        return JsonResponse(
            {
                "tests": tests,
            }
        )
