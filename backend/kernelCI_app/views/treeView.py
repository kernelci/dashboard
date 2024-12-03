from django.http import JsonResponse
from django.views import View
from kernelCI_app.models import Checkouts
from kernelCI_app.serializers import TreeSerializer
from kernelCI_app.utils import getQueryTimeInterval
from kernelCI_app.helpers.errorHandling import ExceptionWithJsonResponse
from kernelCI_app.helpers.date import parseIntervalInDaysGetParameter


DEFAULT_ORIGIN = 'maestro'


class TreeView(View):
    def get(self, request):
        origin_param = request.GET.get('origin', DEFAULT_ORIGIN)
        try:
            interval_days = parseIntervalInDaysGetParameter(
                request.GET.get("intervalInDays", 3)
            )
        except ExceptionWithJsonResponse as e:
            return e.getJsonResponse()

        interval_days_data = {"days": interval_days}

        params = {
            "origin_param": origin_param,
            "interval_param": getQueryTimeInterval(**interval_days_data).timestamp()
        }

        # '1 as id' is necessary in this case because django raw queries must include the primary key.
        # In this case we don't need the primary key and adding it would alter the GROUP BY clause,
        # potentially causing the tree listing page show the same tree multiple times
        checkouts = Checkouts.objects.raw(
            """
            SELECT
                1 as id,
                checkouts.tree_name,
                checkouts.git_repository_branch,
                checkouts.git_repository_url,
                checkouts.git_commit_hash,
                MAX(checkouts.git_commit_name) AS git_commit_name,
                MAX(checkouts.start_time) AS start_time,
                COUNT(DISTINCT CASE WHEN builds.valid = true THEN builds.id END) AS valid_builds,
                COUNT(DISTINCT CASE WHEN builds.valid = false THEN builds.id END) AS invalid_builds,
                COUNT(DISTINCT CASE WHEN builds.valid IS NULL AND builds.id IS NOT NULL THEN builds.id END)
                    AS null_builds,
                COUNT(DISTINCT builds.id) AS total_builds,
                COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
                    AND tests.status = 'FAIL' THEN 1 END) AS fail_tests,
                COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
                    AND tests.status = 'ERROR' THEN 1 END) AS error_tests,
                COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
                    AND tests.status = 'MISS' THEN 1 END) AS miss_tests,
                COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
                    AND tests.status = 'PASS' THEN 1 END) AS pass_tests,
                COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
                    AND tests.status = 'DONE' THEN 1 END) AS done_tests,
                COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
                    AND tests.status = 'SKIP' THEN 1 END) AS skip_tests,
                SUM(CASE WHEN tests.status IS NULL AND tests.id IS NOT NULL THEN 1 ELSE 0 END)
                    AS null_tests,
                COUNT(tests.id) AS total_tests,

                COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
                    AND tests.status = 'FAIL' THEN 1 END) AS fail_boots,
                COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
                    AND tests.status = 'ERROR' THEN 1 END) AS error_boots,
                COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
                    AND tests.status = 'MISS' THEN 1 END) AS miss_boots,
                COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
                    AND tests.status = 'PASS' THEN 1 END) AS pass_boots,
                COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
                    AND tests.status = 'DONE' THEN 1 END) AS done_boots,
                COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
                    AND tests.status = 'SKIP' THEN 1 END) AS skip_boots,
                COALESCE(
                    ARRAY_AGG(DISTINCT tree_name) FILTER (
                        WHERE tree_name IS NOT NULL
                    ),
                    ARRAY[]::TEXT[]
                ) AS tree_names
            FROM
                checkouts
            LEFT JOIN
                builds ON builds.checkout_id = checkouts.id
            LEFT JOIN
                tests ON tests.build_id = builds.id
            WHERE
                checkouts.git_commit_hash IN (
                    SELECT
                        git_commit_hash
                    FROM
                        (
                            SELECT
                                git_repository_branch,
                                git_repository_url,
                                git_commit_hash,
                                ROW_NUMBER() OVER (
                                    PARTITION BY git_repository_url, git_repository_branch
                                    ORDER BY start_time DESC
                                ) AS time_order
                            FROM
                                checkouts
                            WHERE
                                origin = %(origin_param)s
                                AND start_time >= TO_TIMESTAMP(%(interval_param)s)
                        ) AS ordered_checkouts_by_tree
                    WHERE
                        time_order = 1
                    ORDER BY
                        git_repository_branch,
                        git_repository_url,
                        time_order
                )
                AND checkouts.origin = %(origin_param)s
            GROUP BY
                checkouts.git_commit_hash,
                checkouts.git_repository_branch,
                checkouts.git_repository_url,
                checkouts.tree_name
            ORDER BY
                checkouts.git_commit_hash;
            ;
            """, params
        )
        serializer = TreeSerializer(checkouts, many=True)
        resp = JsonResponse(serializer.data, safe=False)
        return resp
