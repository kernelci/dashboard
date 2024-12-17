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
        self.commit_hashes = {}
        self.filterParams = None
        self.field_values = dict()
        self.processed_builds = set()
        self.processed_tests = set()

    def setup_filters(self):
        self.filterTestDurationMin = self.filterParams.filterTestDurationMin
        self.filterTestDurationMax = self.filterParams.filterTestDurationMax
        self.filterBootDurationMin = self.filterParams.filterBootDurationMin
        self.filterBootDurationMax = self.filterParams.filterBootDurationMax
        self.filterBuildDurationMin = self.filterParams.filterBuildDurationMin
        self.filterBuildDurationMax = self.filterParams.filterBuildDurationMax
        self.filterBootStatus = self.filterParams.filterBootStatus
        self.filterTestStatus = self.filterParams.filterTestStatus
        self.filterTreeDetailsConfigs = self.filterParams.filterConfigs
        self.filterTreeDetailsCompiler = self.filterParams.filterCompiler
        self.filterArchitecture = self.filterParams.filterArchitecture
        self.filterHardware = self.filterParams.filterHardware
        self.filterTestPath = self.filterParams.filterTestPath
        self.filterBootPath = self.filterParams.filterBootPath
        self.filterBuildValid = self.filterParams.filterBuildValid

    def sanitize_rows(self, rows: Dict) -> List:
        return [
            {
                "git_commit_hash": row[0],
                "git_commit_name": row[1],
                "earliest_start_time": row[2],
                "build_duration": row[3],
                "architecture": row[4],
                "compiler": row[5],
                "config_name": row[6],
                "build_valid": row[7],
                "test_path": row[8],
                "test_status": row[9],
                "test_duration": row[10],
                "hardware_compatibles": row[11],
                "build_id": row[12],
                "test_id": row[13]
            }
            for row in rows
        ]

    def _create_commit_entry(self) -> Dict:
        return {
            'commit_name': '',
            'builds_count': {
                'true': 0,
                'false': 0,
                'null': 0
            },
            'boots_count': {
                "fail": 0,
                "error": 0,
                "miss": 0,
                "pass": 0,
                "done": 0,
                "skip": 0,
                "null": 0,
            },
            'tests_count': {
                "fail": 0,
                "error": 0,
                "miss": 0,
                "pass": 0,
                "done": 0,
                "skip": 0,
                "null": 0,
            }
        }

    def _process_builds_count(
            self,
            build_valid: bool,
            duration: int,
            commit_hash: str
    ) -> None:
        is_filtered_out = self.filterParams.is_build_filtered_out(
            duration=duration,
            valid=build_valid,
            issue_id=None
        )
        if is_filtered_out:
            return

        label = 'null'
        if build_valid is not None:
            label = str(build_valid).lower()

        self.commit_hashes[commit_hash]['builds_count'][label] += 1

    def _process_boots_count(
        self,
        test_status: str,
        commit_hash: str,
        test_duration: int,
        test_path: str
    ) -> None:
        is_boot_filter_out = self.filterParams.is_boot_filtered_out(
            duration=test_duration,
            issue_id=None,
            path=test_path,
            status=test_status
        )

        if is_boot_filter_out:
            return

        label = test_status.lower()
        self.commit_hashes[commit_hash]['boots_count'][label] += 1

    def _process_nonboots_count(
        self,
        test_status: str,
        commit_hash: str,
        test_duration: int,
        test_path: str
    ) -> None:
        is_nonboot_filter_out = self.filterParams.is_test_filtered_out(
            duration=test_duration,
            issue_id=None,
            path=test_path,
            status=test_status
        )

        if is_nonboot_filter_out:
            return

        label = test_status.lower()
        self.commit_hashes[commit_hash]['tests_count'][label] += 1

    def _pass_in_global_filters(self, row: Dict) -> bool:
        hardware_compatibles = [UNKNOWN_STRING]
        architecture = UNKNOWN_STRING
        compiler = UNKNOWN_STRING
        config_name = UNKNOWN_STRING

        if row['hardware_compatibles'] is not None:
            hardware_compatibles = row['hardware_compatibles']
        if row['architecture'] is not None:
            architecture = row['architecture']
        if row['compiler'] is not None:
            compiler = row['compiler']
        if row['config_name'] is not None:
            config_name = row['config_name']

        if (
            (
                len(self.filterHardware) > 0
                and (not self.filterHardware.intersection(hardware_compatibles))
            )
            or (
                len(self.filterArchitecture) > 0
                and (architecture not in self.filterArchitecture)
            )
            or (
                len(self.filterTreeDetailsCompiler) > 0
                and (compiler not in self.filterTreeDetailsCompiler)
            )
            or (
                len(self.filterTreeDetailsConfigs) > 0
                and (config_name not in self.filterTreeDetailsConfigs)
            )
        ):
            return False

        return True

    def _process_tests(self, row: Dict) -> None:
        if row['test_id'] is not None and row['test_id'] not in self.processed_tests:
            commit_hash = row['git_commit_hash']
            self.processed_tests.add(row['test_id'])
            is_boot = row['test_path'] is not None and row['test_path'].startswith('boot')

            if is_boot:
                self._process_boots_count(
                    row['test_status'] or "NULL",
                    commit_hash,
                    row['test_duration'],
                    row['test_path']
                )
            else:
                self._process_nonboots_count(
                    row['test_status'] or "NULL",
                    commit_hash,
                    row['test_duration'],
                    row['test_path']
                )

    def _process_builds(self, row: Dict) -> None:
        if row["build_id"] is not None and row['build_id'] not in self.processed_builds:
            commit_hash = row['git_commit_hash']
            self.processed_builds.add(row['build_id'])
            self._process_builds_count(row["build_valid"], row['build_duration'], commit_hash)

    def _process_rows(self, rows: Dict) -> None:
        sanitized_rows = self.sanitize_rows(rows)

        for row in sanitized_rows:
            record_filter_out = self.filterParams.is_record_filtered_out(
                hardwares=row['hardware_compatibles'],
                architecture=row['architecture'],
                compiler=row['compiler'],
                config_name=row['config_name']
            )

            if record_filter_out:
                continue

            commit_hash = row['git_commit_hash']
            if commit_hash not in self.commit_hashes:
                self.commit_hashes[commit_hash] = self._create_commit_entry()
                self.commit_hashes[commit_hash]['commit_name'] = row["git_commit_name"]
                self.commit_hashes[commit_hash]['earliest_start_time'] = row["earliest_start_time"]

            self._process_tests(row)
            self._process_builds(row)

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
            self.filterParams = FilterParams(request)
            self.setup_filters()
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
