from django.http import JsonResponse
from rest_framework.views import APIView
from kernelCI_app.models import Builds


class BuildStatusCountView(APIView):
    def get(self, _request, build_id):
        builds = Builds.objects.raw(
            """
            SELECT
                builds.id, builds.log_excerpt,
                COUNT(CASE WHEN tests.status = 'FAIL' THEN 1 END) AS fail_tests,
                COUNT(CASE WHEN tests.status = 'ERROR' THEN 1 END) AS error_tests,
                COUNT(CASE WHEN tests.status = 'MISS' THEN 1 END) AS miss_tests,
                COUNT(CASE WHEN tests.status = 'PASS' THEN 1 END) AS pass_tests,
                COUNT(CASE WHEN tests.status = 'DONE' THEN 1 END) AS done_tests,
                COUNT(CASE WHEN tests.status = 'SKIP' THEN 1 END) AS skip_tests,
                SUM(CASE WHEN tests.status IS NULL AND tests.id IS NOT NULL THEN 1 ELSE 0 END)
                    AS null_tests,
                COUNT(tests.id) AS total_tests
            FROM
                builds
            LEFT JOIN
                tests ON tests.build_id = builds.id
            WHERE builds.id = %s
            GROUP BY builds.id, builds.log_excerpt;
            """,
            [build_id],
        )

        build_status_counts = list(builds)
        if not build_status_counts:
            return JsonResponse({"error": "Build not found"}, status=404)

        build_status = build_status_counts[0]
        log_excerpt = build_status.log_excerpt
        build_counts = {
            "build_id": build_status.id,
            "fail_tests": build_status.fail_tests,
            "error_tests": build_status.error_tests,
            "miss_tests": build_status.miss_tests,
            "pass_tests": build_status.pass_tests,
            "done_tests": build_status.done_tests,
            "skip_tests": build_status.skip_tests,
            "null_tests": build_status.null_tests,
            "total_tests": build_status.total_tests,
        }

        return JsonResponse({"log_excerpt": log_excerpt, "build_counts": build_counts})
