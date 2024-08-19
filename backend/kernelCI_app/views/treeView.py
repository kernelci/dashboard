from django.http import JsonResponse
from django.views import View
from kernelCI_app.models import Checkouts
from kernelCI_app.serializers import TreeSerializer
from kernelCI_app.utils import getQueryTimeInterval


DEFAULT_ORIGIN = '0dayci'


class TreeView(View):
    def get(self, request):
        origin = request.GET.get('origin', DEFAULT_ORIGIN)

        checkouts = Checkouts.objects.raw(
            """
            WITH selection AS (
                SELECT
                    git_repository_url,
                    git_repository_branch,
                    MAX(start_time) AS start_time
                FROM
                    (
                        SELECT
                            git_repository_url,
                            git_repository_branch,
                            origin,
                            start_time
                        FROM
                            checkouts
                        WHERE
                            origin = %s AND start_time  >= TO_TIMESTAMP(%s)
                        ORDER BY
                            start_time DESC
                    ) AS selection_sorted
                GROUP BY
                    git_repository_url, git_repository_branch
                ORDER BY
                    start_time DESC
            )

            SELECT
                checkouts.*,
                COUNT(DISTINCT CASE WHEN builds.valid = true THEN builds.id END) AS valid_builds,
                COUNT(DISTINCT CASE WHEN builds.valid = false THEN builds.id END) AS invalid_builds,
                COUNT(DISTINCT CASE WHEN builds.valid IS NULL AND builds.id IS NOT NULL THEN builds.id END)
                    AS null_builds,
                COUNT(DISTINCT builds.id) AS total_builds,
                COUNT(CASE WHEN tests.status = 'FAIL' THEN 1 END) AS fail_tests,
                COUNT(CASE WHEN tests.status = 'ERROR' THEN 1 END) AS error_tests,
                COUNT(CASE WHEN tests.status = 'MISS' THEN 1 END) AS miss_tests,
                COUNT(CASE WHEN tests.status = 'PASS' THEN 1 END) AS pass_tests,
                COUNT(CASE WHEN tests.status = 'DONE' THEN 1 END) AS done_tests,
                COUNT(CASE WHEN tests.status = 'SKIP' THEN 1 END) AS skip_tests,
                SUM(CASE WHEN tests.status IS NULL AND tests.id IS NOT NULL THEN 1 ELSE 0 END)
                    AS null_tests,
                COUNT(tests.id) AS total_tests,
                COALESCE(
                    ARRAY_AGG(DISTINCT tree_name) FILTER (WHERE tree_name IS NOT NULL),
                    ARRAY[]::text[]
                ) AS tree_names
            FROM
                selection
            JOIN checkouts ON
                checkouts.git_repository_url = selection.git_repository_url AND
                checkouts.git_repository_branch = selection.git_repository_branch AND
                checkouts.start_time = selection.start_time
            LEFT JOIN
                builds ON builds.checkout_id = checkouts.id
            LEFT JOIN
                tests ON tests.build_id = builds.id
            GROUP BY
                checkouts.id
            ORDER BY
                checkouts.start_time DESC;
            ;
            """, [origin, getQueryTimeInterval().timestamp()]
        )

        serializer = TreeSerializer(checkouts, many=True)
        resp = JsonResponse(serializer.data, safe=False)
        return resp
