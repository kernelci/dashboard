from django.http import HttpResponseNotFound, JsonResponse
from django.views import View
from django.db import connection


class Test(View):
    def get(self, _, commit_hash):
        with connection.cursor() as cursor:
            cursor.execute("""
                WITH r AS (
                        SELECT
                            tests.status,
                            tests.id AS testId,
                            tests._timestamp AS testTimestamp,
                            builds.config_name AS config,
                            tests.log_excerpt AS log
                        FROM checkouts
                            checkouts
                        LEFT JOIN builds ON
                            builds.checkout_id = checkouts.id
                        LEFT JOIN tests ON
                            tests.build_id = builds.id
                        WHERE
                            checkouts.git_commit_hash = '%s'),
                    testsSummary AS (
                        SELECT
                            COUNT(CASE WHEN r.status = 'FAIL' THEN 1 END) AS fail_tests,
                            COUNT(CASE WHEN r.status = 'ERROR' THEN 1 END) AS error_tests,
                            COUNT(CASE WHEN r.status = 'MISS' THEN 1 END) AS miss_tests,
                            COUNT(CASE WHEN r.status = 'PASS' THEN 1 END) AS pass_tests,
                            COUNT(CASE WHEN r.status = 'DONE' THEN 1 END) AS done_tests,
                            COUNT(CASE WHEN r.status = 'SKIP' THEN 1 END) AS skip_tests,
                            SUM(CASE WHEN r.status IS NULL AND r.testId IS NOT NULL THEN 1 ELSE 0 END)
                                AS null_tests,
                            COUNT(r.testId) AS total_tests
                        FROM r
                    ),
                    testsConfig AS (
                        SELECT
                            r.config,
                            COUNT(r.config)
                        FROM r
                        GROUP BY r.config
                    ),
                    errorSummary AS (
                        SELECT
                            r.log
                        FROM r
                        WHERE r.status = 'ERROR'
                    ),
                    combined AS (
                        SELECT
                            (SELECT json_agg(testsSummary) AS testsSummary FROM testsSummary),
                            (SELECT json_agg(testsConfig) AS testsConfig FROM testsConfig),
                            (SELECT json_agg(errorSummary) AS errorSummary FROM errorSummary)
                    )

                SELECT 1 AS id, testsSummary, testsConfig, errorSummary FROM combined;
                """ % commit_hash)
            results = cursor.fetchone()
            if results is not None:
                return JsonResponse({
                    "id": results[0],
                    "statusCount": results[1][0],
                    "testsConfig": results[2],
                    "errorSummary": results[3],
                }, safe=False)

                # return JsonResponse(results, safe=False)
        return HttpResponseNotFound('{}')
