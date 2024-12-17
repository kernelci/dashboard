from kernelCI_app.utils import (
    getErrorResponseBody
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse, HttpResponseBadRequest
from django.db import connection
from typing import Dict, List
from kernelCI_app.helpers.filters import (
    UNKNOWN_STRING,
    FilterParams,
    InvalidComparisonOP
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

        if (isinstance(filter['value'], str) and filter['value'] in NULL_STRINGS):
            return is_null_clause
        else:
            if ('NULL' in filter['value']):
                has_null_value = True
                filter['value'].remove('NULL')
            elif ('Unknown' in filter['value']):
                has_null_value = True
                filter['value'].remove('Unknown')

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

            # temporary solution since the query isn't joining on issues table
            if field == "issue":
                continue

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

        query = """
        WITH earliest_commits AS (
            SELECT
                 id,
                git_commit_hash,
                git_commit_name,
                git_repository_branch,
                git_repository_url,
                origin,
                start_time,
                time_order
            FROM (
                SELECT
                    id,
                    git_commit_hash,
                    git_commit_name,
                    git_repository_branch,
                    git_repository_url,
                    origin,
                    start_time,
                    ROW_NUMBER() OVER (
                        PARTITION BY git_repository_url, git_repository_branch, origin, git_commit_hash
                        ORDER BY start_time DESC
                    ) AS time_order
                FROM   checkouts
                WHERE  git_repository_branch = %(git_branch_param)s
                    AND git_repository_url = %(git_url_param)s
                    AND origin = %(origin_param)s
                    AND git_commit_hash IS NOT NULL
                    AND start_time <= (SELECT Max(start_time) AS head_start_time
                                        FROM   checkouts
                                        WHERE  git_commit_hash = %(commit_hash)s
                                                AND origin = %(origin_param)s
                                                AND git_repository_url = %(git_url_param)s)
                ORDER  BY start_time DESC) AS checkouts_time_order
            WHERE
                time_order = 1
            LIMIT 6
        )
        SELECT
            c.git_commit_hash,
            c.git_commit_name,
            c.start_time,
            b.duration,
            b.architecture,
            b.compiler,
            b.config_name,
            b.valid,
            t.path,
            t.status,
            t.duration,
            t.environment_compatible,
            b.id AS build_id,
            t.id AS test_id
        FROM earliest_commits AS c
        INNER JOIN builds AS b
        ON
            c.id = b.checkout_id
        LEFT JOIN tests AS t
        ON
            t.build_id = b.id
        """

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                self.field_values,
            )
            rows = cursor.fetchall()

        self._process_rows(rows)
        # Format the results as JSON
        results = []

        for key, value in self.commit_hashes.items():
            results.append({
                "git_commit_hash": key,
                "git_commit_name": value['commit_name'],
                "earliest_start_time": value['earliest_start_time'],
                "builds": {
                    "valid_builds": value['builds_count']['true'],
                    "invalid_builds": value['builds_count']['false'],
                    "null_builds": value['builds_count']['null'],
                },
                "boots_tests": {
                    "fail_count": value['boots_count']['fail'],
                    "error_count": value['boots_count']['error'],
                    "miss_count": value['boots_count']['miss'],
                    "pass_count": value['boots_count']['pass'],
                    "done_count": value['boots_count']['done'],
                    "skip_count": value['boots_count']['skip'],
                    "null_count": value['boots_count']['null'],
                },
                "non_boots_tests": {
                    "fail_count": value['tests_count']['fail'],
                    "error_count": value['tests_count']['error'],
                    "miss_count": value['tests_count']['miss'],
                    "pass_count": value['tests_count']['pass'],
                    "done_count": value['tests_count']['done'],
                    "skip_count": value['tests_count']['skip'],
                    "null_count": value['tests_count']['null'],
                },
            })

        return JsonResponse(results, safe=False)
