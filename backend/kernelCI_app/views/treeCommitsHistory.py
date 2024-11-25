from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse, HttpResponseBadRequest
from django.db import connection
from kernelCI_app.utils import (
    FilterParams,
    InvalidComparisonOP,
    getErrorResponseBody,
)


# TODO Move this endpoint to a function so it doesn't
# have to be another request, it can be called from the tree details endpoint
class TreeCommitsHistory(APIView):
    def __init__(self):
        self.filters_options = {
            'build': {
                'table_alias': 'b',
                'filters': []
            },
            'boot': {
                'table_alias': 't',
                'filters': []
            },
            'test': {
                'table_alias': 't',
                'filters': []
            }
        }
        self.field_values = dict()

    def __format_field_operation(self, f, filter_params):
        split_filter = f['field'].split('.')

        if len(split_filter) == 1:
            split_filter.insert(0, 'build')

        table, field = split_filter

        field = field.replace("[]", "")

        if (field == "hardware"):
            field = "environment_compatible"
            op = "&&"
            if isinstance(f['value'], str):
                f['value'] = [f['value']]
        else:
            op = filter_params.get_comparison_op(f, "raw")

        return table, field, op

    def __treat_unknown_filter(self, table_field, op, value_name, filter):
        clause = table_field
        is_null_clause = f"{table_field} IS NULL"
        has_null_value = False
        if (isinstance(filter['value'], str)):
            filter['value'] = '' if filter['value'] in ['NULL', 'Unknown'] else filter['value']
        else:
            if ('NULL' in filter['value']):
                has_null_value = True
                filter['value'].remove('NULL')
            elif ('Unknown' in filter['value']):
                has_null_value = True
                filter['value'].remove('Unknown')

        if (len(filter['value']) == 0):
            clause = is_null_clause
        else:
            self.field_values[value_name] = filter['value']
            if op == "IN":
                clause += f" = ANY(%({value_name})s)"
            elif op == "LIKE":
                self.field_values[value_name] = f"%{filter['value']}%"
                clause += f" {op} %({value_name})s"
            else:
                clause += f" {op} %({value_name})s"

            if has_null_value:
                clause += f" OR {is_null_clause}"
        return clause

    # TODO: unite the filters logic
    def __get_filters(self, filter_params):
        grouped_filters = filter_params.get_grouped_filters()

        for _, filter in grouped_filters.items():
            table, field, op = self.__format_field_operation(filter, filter_params)

            table_field = f"{self.filters_options[table]['table_alias']}.{field}"
            value_name = f"{table}{field.capitalize()}{filter_params.get_comparison_op(filter)}"
            clause = self.__treat_unknown_filter(table_field, op, value_name, filter)

            if field != "environment_compatible":
                self.filters_options[table]['filters'].append(clause)

            if field in ["config_name", "architecture", "compiler", "environment_compatible"]:
                self.filters_options['test']['filters'].append(clause)
                self.filters_options['boot']['filters'].append(clause)

        build_counts_where = """
            c.git_repository_branch = %(git_branch_param)s
            AND c.git_repository_url = %(git_url_param)s
            AND c.origin = %(origin_param)s"""

        boot_counts_where = """
            b.start_time >= (
                SELECT
                    MIN(earliest_start_time)
                FROM earliest_commits
            )
            AND t.start_time >= (
                SELECT
                    MIN(earliest_start_time)
                FROM earliest_commits
            )"""

        test_counts_where = """
            b.start_time >= (
                SELECT
                    MIN(earliest_start_time)
                FROM earliest_commits
            )
            AND t.start_time >= (
                SELECT
                    MIN(earliest_start_time)
                FROM earliest_commits
            )"""

        if len(self.filters_options['build']['filters']) > 0:
            filter_clauses = f"""
                AND {" AND ".join(self.filters_options['build']['filters'])}"""
            build_counts_where += filter_clauses

        if len(self.filters_options['boot']['filters']) > 0:
            filter_clauses = f"""
                AND {" AND ".join(self.filters_options['boot']['filters'])}"""
            boot_counts_where += filter_clauses

        if len(self.filters_options['test']['filters']) > 0:
            filter_clauses = f"""
                AND {" AND ".join(self.filters_options['test']['filters'])}"""
            test_counts_where += filter_clauses

        return (
            build_counts_where,
            boot_counts_where,
            test_counts_where
        )

    def get(self, request, commit_hash):
        origin_param = request.GET.get("origin")
        git_url_param = request.GET.get("git_url")
        git_branch_param = request.GET.get("git_branch")

        missing_params = []
        if not origin_param:
            missing_params.append("origin")
        if not git_url_param:
            missing_params.append("git_url")
        if not git_branch_param:
            missing_params.append("git_branch")

        if missing_params:
            return Response(
                {"error": f"Missing parameters: {', '.join(missing_params)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            filter_params = FilterParams(request)
        except InvalidComparisonOP as e:
            return HttpResponseBadRequest(getErrorResponseBody(str(e)))

        self.field_values = {
            "commit_hash": commit_hash,
            "origin_param": origin_param,
            "git_url_param": git_url_param,
            "git_branch_param": git_branch_param,
        }

        build_counts_where, boot_counts_where, test_counts_where = self.__get_filters(filter_params)

        query = f"""
        WITH
        relevant_checkouts AS (
            SELECT
                id,
                git_commit_hash,
                git_commit_name,
                git_repository_branch,
                git_repository_url,
                origin,
                start_time
            FROM
                checkouts
            WHERE
                git_repository_branch = %(git_branch_param)s
                AND git_repository_url = %(git_url_param)s
                AND origin = %(origin_param)s
            ORDER BY
                start_time DESC
        ),
        earliest_commits AS (
            SELECT
                git_commit_hash,
                git_commit_name,
                MAX(start_time) AS earliest_start_time
            FROM
                relevant_checkouts
            GROUP BY
                git_commit_hash,
                git_commit_name
            ORDER BY
                earliest_start_time DESC
            LIMIT 6
        ),
        build_counts AS (
            SELECT
                c.git_commit_hash,
                SUM(CASE WHEN b.valid = true THEN 1 ELSE 0 END) AS valid_builds,
                SUM(CASE WHEN b.valid = false THEN 1 ELSE 0 END) AS invalid_builds,
                SUM(CASE WHEN b.valid IS NULL THEN 1 ELSE 0 END) AS null_builds
            FROM
                relevant_checkouts AS c
            INNER JOIN
                builds AS b
                ON c.id = b.checkout_id
            WHERE
                {build_counts_where}
            GROUP BY
                c.git_commit_hash
        ),
        boots_counts AS (
            SELECT
                c.git_commit_hash,
                SUM(CASE WHEN t.status = 'FAIL'
                    AND (t.path = 'boot' OR t.path LIKE 'boot.%%') THEN 1 ELSE 0 END)
                    AS boots_fail_count,
                SUM(CASE WHEN t.status = 'ERROR'
                    AND (t.path = 'boot' OR t.path LIKE 'boot.%%') THEN 1 ELSE 0 END)
                    AS boots_error_count,
                SUM(CASE WHEN t.status = 'MISS'
                    AND (t.path = 'boot' OR t.path LIKE 'boot.%%') THEN 1 ELSE 0 END)
                    AS boots_miss_count,
                SUM(CASE WHEN t.status = 'PASS'
                    AND (t.path = 'boot' OR t.path LIKE 'boot.%%') THEN 1 ELSE 0 END)
                    AS boots_pass_count,
                SUM(CASE WHEN t.status = 'DONE'
                    AND (t.path = 'boot' OR t.path LIKE 'boot.%%') THEN 1 ELSE 0 END)
                    AS boots_done_count,
                SUM(CASE WHEN t.status = 'SKIP'
                    AND (t.path = 'boot' OR t.path LIKE 'boot.%%') THEN 1 ELSE 0 END)
                    AS boots_skip_count,
                SUM(CASE WHEN t.status IS NULL
                    AND (t.path = 'boot' OR t.path LIKE 'boot.%%') THEN 1 ELSE 0 END)
                    AS boots_null_count
            FROM
                relevant_checkouts AS c
            INNER JOIN
                builds AS b
                ON
                c.id = b.checkout_id
            LEFT JOIN
                tests AS t
                ON b.id = t.build_id
            WHERE
                {boot_counts_where}
            GROUP BY
                c.git_commit_hash
        ),
        test_counts AS (
            SELECT
                c.git_commit_hash,
                SUM(CASE WHEN t.status = 'FAIL' AND (t.path <> 'boot' AND t.path NOT LIKE 'boot.%%')
                    THEN 1 ELSE 0 END) AS non_boots_fail_count,
                SUM(CASE WHEN t.status = 'ERROR' AND (t.path <> 'boot' AND t.path NOT LIKE 'boot.%%')
                    THEN 1 ELSE 0 END) AS non_boots_error_count,
                SUM(CASE WHEN t.status = 'MISS' AND (t.path <> 'boot' AND t.path NOT LIKE 'boot.%%')
                    THEN 1 ELSE 0 END) AS non_boots_miss_count,
                SUM(CASE WHEN t.status = 'PASS' AND (t.path <> 'boot' AND t.path NOT LIKE 'boot.%%')
                    THEN 1 ELSE 0 END) AS non_boots_pass_count,
                SUM(CASE WHEN t.status = 'DONE' AND (t.path <> 'boot' AND t.path NOT LIKE 'boot.%%')
                    THEN 1 ELSE 0 END) AS non_boots_done_count,
                SUM(CASE WHEN t.status = 'SKIP' AND (t.path <> 'boot' AND t.path NOT LIKE 'boot.%%')
                    THEN 1 ELSE 0 END) AS non_boots_skip_count,
                SUM(CASE WHEN t.status IS NULL AND (t.path <> 'boot' AND t.path NOT LIKE 'boot.%%')
                    THEN 1 ELSE 0 END) AS non_boots_null_count
            FROM
                relevant_checkouts AS c
            INNER JOIN
                builds AS b
                ON
                c.id = b.checkout_id
            LEFT JOIN
                tests AS t
                ON b.id = t.build_id
            WHERE
                {test_counts_where}
            GROUP BY
                c.git_commit_hash
        )
        SELECT
            ec.git_commit_hash,
            ec.git_commit_name,
            ec.earliest_start_time,
            bc.valid_builds,
            bc.invalid_builds,
            bc.null_builds,
            boc.boots_fail_count,
            boc.boots_error_count,
            boc.boots_miss_count,
            boc.boots_pass_count,
            boc.boots_done_count,
            boc.boots_skip_count,
            boc.boots_null_count,
            tc.non_boots_fail_count,
            tc.non_boots_error_count,
            tc.non_boots_miss_count,
            tc.non_boots_pass_count,
            tc.non_boots_done_count,
            tc.non_boots_skip_count,
            tc.non_boots_null_count
        FROM
            earliest_commits AS ec
        LEFT JOIN
            build_counts AS bc
            ON ec.git_commit_hash = bc.git_commit_hash
        LEFT JOIN
            boots_counts AS boc
            ON ec.git_commit_hash = boc.git_commit_hash
        LEFT JOIN
            test_counts AS tc
            ON ec.git_commit_hash = tc.git_commit_hash
        ORDER BY
            ec.earliest_start_time DESC
        LIMIT 6;
        """

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                self.field_values,
            )
            rows = cursor.fetchall()

        # Format the results as JSON
        results = [
            {
                "git_commit_hash": row[0],
                "git_commit_name": row[1],
                "earliest_start_time": row[2],
                "builds": {
                    "valid_builds": row[3] or 0,
                    "invalid_builds": row[4] or 0,
                    "null_builds": row[5] or 0,
                },
                "boots_tests": {
                    "fail_count": row[6] or 0,
                    "error_count": row[7] or 0,
                    "miss_count": row[8] or 0,
                    "pass_count": row[9] or 0,
                    "done_count": row[10] or 0,
                    "skip_count": row[11] or 0,
                    "null_count": row[12] or 0,
                },
                "non_boots_tests": {
                    "fail_count": row[13] or 0,
                    "error_count": row[14] or 0,
                    "miss_count": row[15] or 0,
                    "pass_count": row[16] or 0,
                    "done_count": row[17] or 0,
                    "skip_count": row[18] or 0,
                    "null_count": row[19] or 0,
                },
            }
            for row in rows
        ]

        return JsonResponse(results, safe=False)
