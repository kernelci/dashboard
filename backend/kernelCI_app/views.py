from django.http import JsonResponse
from django.views import View

from kernelCI_app.models import Checkouts
from kernelCI_app.serializers import TreeSerializer
from kernelCI_app.utils import get_visible_record_ids


class TreeView(View):

    def get(self, _):
        checkout_ids = get_visible_record_ids('checkouts')
        placeholders = ','.join(['%s'] * len(checkout_ids))

        checkouts = Checkouts.objects.raw(f"""
            SELECT
                checkouts.*,
                COUNT(CASE WHEN builds.valid = true THEN 1 END) AS valid_builds,
                COUNT(CASE WHEN builds.valid = false THEN 1 END) AS invalid_builds,
                SUM(CASE WHEN builds.valid IS NULL AND builds.id IS NOT NULL THEN 1 ELSE 0 END)
                    AS null_builds,
                COUNT(builds.id) AS total_builds,
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
            WHERE
                checkouts.id IN ({placeholders})
            GROUP BY
                checkouts.id;
            """,
            checkout_ids
        )

        for c in checkouts:
            print('checkout:', c.id, c.valid_builds, c.pass_tests)

        serializer = TreeSerializer(checkouts, many=True)
        resp = JsonResponse(serializer.data, safe=False)
        return resp
