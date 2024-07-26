from django.http import JsonResponse
from django.views import View
from kernelCI_app.models import Checkouts
from kernelCI_app.serializers import TreeSerializer
from kernelCI_app.utils import get_visible_record_identifiers


class TreeView(View):

    def get(self, _):
        commit_hashs = get_visible_record_identifiers('checkouts')
        placeholders = ','.join(['%s'] * len(commit_hashs))

        checkouts = Checkouts.objects.raw(
            f"""
            SELECT
                checkouts.git_commit_hash AS id,
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
                COUNT(tests.id) AS total_tests
            FROM
                checkouts
            LEFT JOIN
                builds ON builds.checkout_id = checkouts.id
            LEFT JOIN
                tests ON tests.build_id = builds.id
            WHERE checkouts.git_commit_hash IN ({placeholders})
            GROUP BY
                checkouts.git_commit_hash;
            """,
            commit_hashs
        )

        serializer = TreeSerializer(checkouts, many=True)
        resp = JsonResponse(serializer.data, safe=False)
        return resp
