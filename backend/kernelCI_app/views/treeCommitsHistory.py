from datetime import datetime, timezone
from http import HTTPStatus

from django.http import HttpRequest
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.filters import (
    FilterParams,
    InvalidComparisonOPError,
)
from kernelCI_app.constants.general import UNCATEGORIZED_STRING, UNKNOWN_STRING
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.helpers.misc import (
    handle_misc,
    misc_value_or_default,
)
from kernelCI_app.typeModels.commonOpenApiParameters import (
    COMMIT_HASH_PATH_PARAM,
    GIT_BRANCH_PATH_PARAM,
    TREE_NAME_PATH_PARAM,
)
from kernelCI_app.typeModels.databases import FAIL_STATUS, NULL_STATUS, StatusValues
from kernelCI_app.utils import is_boot, sanitize_dict
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from typing import Optional
from kernelCI_app.typeModels.treeCommits import (
    DirectTreeCommitsQueryParameters,
    TreeCommitsQueryParameters,
    TreeCommitsResponse,
    TreeEntityTypes,
)
from pydantic import ValidationError
from kernelCI_app.constants.general import MAESTRO_DUMMY_BUILD_PREFIX
from kernelCI_app.queries.tree import get_tree_commit_history
from kernelCI_app.constants.localization import ClientStrings


# TODO Move this endpoint to a function so it doesn't
# have to be another request, it can be called from the tree details endpoint
class BaseTreeCommitsHistory(APIView):
    def __init__(self):
        self.commit_hashes = {}
        self.filterParams = None
        self.start_datetime = None
        self.end_datetime = None
        self.processed_builds = set()
        self.processed_tests = set()
        self.builds_related_to_filtered_tests_only = False

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
        self.filter_lab = self.filterParams.filter_labs
        self.filterTestPath = self.filterParams.filterTestPath
        self.filterBootPath = self.filterParams.filterBootPath
        self.filterBuildStatus = self.filterParams.filterBuildStatus

    # TODO: use a pydantic model instead of a dict
    def sanitize_rows(self, rows: dict) -> list:
        result = []
        for row in rows:
            build_misc = row[11]
            sanitized_build_misc = sanitize_dict(build_misc)
            build_lab = (
                sanitized_build_misc.get("lab", UNKNOWN_STRING)
                if sanitized_build_misc
                else UNKNOWN_STRING
            )

            result.append(
                {
                    "git_commit_hash": row[0],
                    "git_commit_name": row[1],
                    "git_commit_tags": row[2],
                    "earliest_start_time": row[3],
                    "build_duration": row[4],
                    "architecture": row[5],
                    "compiler": row[6],
                    "config_name": row[7],
                    "build_status": NULL_STATUS if row[8] is None else row[8],
                    "build_origin": row[9],
                    "build_id": row[10],
                    "build_misc": build_misc,
                    "test_path": row[12],
                    "test_status": row[13],
                    "test_duration": row[14],
                    "hardware_compatibles": row[15],
                    "test_environment_misc": row[16],
                    "test_origin": row[17],
                    "test_lab": row[18],
                    "test_id": row[19],
                    "incidents_id": row[20],
                    "incidents_test_id": row[21],
                    "issue_id": row[22],
                    "issue_version": row[23],
                    "build_lab": build_lab,
                }
            )

        return result

    def _create_commit_entry(self) -> dict:
        empty_status_dict = {
            "fail": 0,
            "error": 0,
            "miss": 0,
            "pass": 0,
            "done": 0,
            "skip": 0,
            "null": 0,
        }

        return {
            "commit_name": "",
            "builds_count": dict(empty_status_dict),
            "boots_count": dict(empty_status_dict),
            "tests_count": dict(empty_status_dict),
        }

    def _process_builds_count(
        self,
        *,
        build_status: StatusValues,
        duration: int,
        commit_hash: str,
        issue_id: str,
        issue_version: int,
        incident_test_id: Optional[str],
        key: str,
        build_origin: str,
    ) -> None:
        is_filtered_out = self.filterParams.is_build_filtered_out(
            duration=duration,
            build_status=build_status,
            issue_id=issue_id,
            issue_version=issue_version,
            incident_test_id=incident_test_id,
            build_origin=build_origin,
        )
        if is_filtered_out:
            return

        self.processed_builds.add(key)

        label = build_status.lower()
        self.commit_hashes[commit_hash]["builds_count"][label] += 1

    def _process_boots_count(
        self,
        *,
        test_id: str,
        test_status: str,
        commit_hash: str,
    ) -> None:
        is_boot_processed = test_id in self.processed_tests

        if is_boot_processed:
            return

        self.processed_tests.add(test_id)
        label = test_status.lower()
        self.commit_hashes[commit_hash]["boots_count"][label] += 1

    def _process_nonboots_count(
        self,
        *,
        test_id: str,
        test_status: str,
        commit_hash: str,
    ) -> None:
        is_test_processed = test_id in self.processed_tests

        if is_test_processed:
            return

        self.processed_tests.add(test_id)
        label = test_status.lower()
        self.commit_hashes[commit_hash]["tests_count"][label] += 1

    def _pass_in_global_filters(self, row: dict) -> bool:
        hardware_compatibles = [UNKNOWN_STRING]
        architecture = UNKNOWN_STRING
        compiler = UNKNOWN_STRING
        config_name = UNKNOWN_STRING

        if row["hardware_compatibles"] is not None:
            hardware_compatibles = row["hardware_compatibles"]
        if row["architecture"] is not None:
            architecture = row["architecture"]
        if row["compiler"] is not None:
            compiler = row["compiler"]
        if row["config_name"] is not None:
            config_name = row["config_name"]

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

    def _process_tests(self, row: dict) -> None:
        test_id = row["test_id"]
        test_status = row["test_status"] or "NULL"
        test_path = row["test_path"]
        commit_hash = row["git_commit_hash"]

        if test_id is None:
            return

        if is_boot(test_path):
            self._process_boots_count(
                test_id=test_id,
                test_status=test_status,
                commit_hash=commit_hash,
            )
        else:
            self._process_nonboots_count(
                test_id=test_id,
                test_status=test_status,
                commit_hash=commit_hash,
            )

    def _process_builds(self, row: dict) -> None:
        build_id = row["build_id"]
        if build_id is None:
            return
        commit_hash = row["git_commit_hash"]
        build_origin = row["build_origin"]

        key = f"{build_id}_{commit_hash}"

        if (
            build_id is not None
            and key not in self.processed_builds
            and not build_id.startswith(MAESTRO_DUMMY_BUILD_PREFIX)
        ):
            self._process_builds_count(
                build_status=row["build_status"],
                duration=row["build_duration"],
                commit_hash=commit_hash,
                issue_id=row["issue_id"],
                issue_version=row["issue_version"],
                incident_test_id=row["incidents_test_id"],
                key=key,
                build_origin=build_origin,
            )

    def _is_record_in_time_period(self, start_time: datetime) -> bool:
        if self.start_datetime is not None and self.end_datetime is not None:
            return start_time >= self.start_datetime and start_time <= self.end_datetime
        return True

    def _is_test_row_filtered_out(self, row: dict) -> bool:
        test_id = row["test_id"]
        if test_id is None:
            return True

        issue_id = row["issue_id"]
        test_status = row["test_status"] or "NULL"
        test_duration = row["test_duration"]
        test_path = row["test_path"]
        issue_version = row["issue_version"]
        incident_test_id = row["incidents_test_id"]
        build_status = row["build_status"]
        test_origin = row["test_origin"]

        if issue_id is None and (
            build_status in [FAIL_STATUS, NULL_STATUS] or test_status == FAIL_STATUS
        ):
            issue_id = UNCATEGORIZED_STRING

        if is_boot(test_path):
            return self.filterParams.is_boot_filtered_out(
                duration=test_duration,
                issue_id=issue_id,
                issue_version=issue_version,
                path=test_path,
                status=test_status,
                incident_test_id=incident_test_id,
                origin=test_origin,
            )

        return self.filterParams.is_test_filtered_out(
            duration=test_duration,
            issue_id=issue_id,
            issue_version=issue_version,
            path=test_path,
            status=test_status,
            incident_test_id=incident_test_id,
            origin=test_origin,
        )

    def _process_rows(self, rows: dict, requested_types: list[TreeEntityTypes]) -> None:
        sanitized_rows = self.sanitize_rows(rows)

        for row in sanitized_rows:
            test_environment_misc = handle_misc(row["test_environment_misc"])

            hardware_filter = []
            if row["hardware_compatibles"] is not None:
                hardware_filter = row["hardware_compatibles"]
            if test_environment_misc is not None:
                platform = misc_value_or_default(test_environment_misc).get("platform")
                if platform and str(platform).lower() != UNKNOWN_STRING.lower():
                    hardware_filter.append(platform)
            # Only consider build platform if there is neither compatibles nor env platform
            if len(hardware_filter) == 0:
                build_misc = handle_misc(row["build_misc"])
                hardware_filter = [misc_value_or_default(build_misc).get("platform")]

            record_in_period = self._is_record_in_time_period(
                start_time=row["earliest_start_time"]
            )

            record_filter_out = (
                not record_in_period
                or self.filterParams.is_record_filtered_out(
                    hardwares=hardware_filter,
                    architecture=row["architecture"],
                    compiler=row["compiler"],
                    config_name=row["config_name"],
                    lab=row["test_lab"],
                )
            )

            is_record_checkout_only = row["build_id"] is None and row["test_id"] is None

            if record_filter_out and not is_record_checkout_only:
                continue

            commit_hash = row["git_commit_hash"]
            if commit_hash not in self.commit_hashes:
                self.commit_hashes[commit_hash] = self._create_commit_entry()
                self.commit_hashes[commit_hash]["commit_name"] = row["git_commit_name"]
                self.commit_hashes[commit_hash]["commit_tags"] = row["git_commit_tags"]
                self.commit_hashes[commit_hash]["earliest_start_time"] = row[
                    "earliest_start_time"
                ]

            is_test_filtered_out = self._is_test_row_filtered_out(row)

            # Ignore the boots/tests counts if we just asked for builds
            if not requested_types == ["builds"] and not is_test_filtered_out:
                self._process_tests(row)

            # Only process the builds if either we allow any build or
            # if we only asked for builds related to tests that passed the filter and it did
            if self.builds_related_to_filtered_tests_only and is_test_filtered_out:
                continue
            self._process_builds(row)

    def _process_time_range(self, *, start_timestamp: str, end_timestamp: str) -> None:
        try:
            self.end_datetime = datetime.fromtimestamp(int(end_timestamp), timezone.utc)
            self.start_datetime = datetime.fromtimestamp(
                int(start_timestamp), timezone.utc
            )
        except Exception as ex:
            log_message(ex)

    # TODO: lower the complexity of this function
    def get(  # noqa: C901
        self,
        request: HttpRequest,
        commit_hash: str,
        tree_name: Optional[str] = None,
        git_branch: Optional[str] = None,
    ) -> Response:
        try:
            params = TreeCommitsQueryParameters(
                origin=request.GET.get("origin"),
                git_url=request.GET.get("git_url"),
                git_branch=request.GET.get("git_branch"),
                start_timestamp_in_seconds=request.GET.get(
                    "start_timestamp_in_seconds"
                ),
                end_timestamp_in_seconds=request.GET.get("end_timestamp_in_seconds"),
                types=request.GET.get("types"),
                builds_related_to_filtered_tests_only=request.GET.get(
                    "builds_related_to_filtered_tests_only", False
                ),
            )
        except ValidationError as e:
            return create_api_error_response(error_message=e.json())

        start_timestamp = params.start_timestamp_in_seconds
        end_timestamp = params.end_timestamp_in_seconds
        if None not in (start_timestamp, end_timestamp):
            self._process_time_range(
                start_timestamp=start_timestamp, end_timestamp=end_timestamp
            )

        try:
            self.filterParams = FilterParams(request)
            self.setup_filters()
        except InvalidComparisonOPError as e:
            return create_api_error_response(error_message=str(e))

        # When relation-gated builds mode is enabled we need tests/boots rows to identify
        # which builds are related to filtered tests.
        self.builds_related_to_filtered_tests_only = (
            params.builds_related_to_filtered_tests_only
        )

        include_types = params.types
        if params.types == ["builds"] and (
            self.builds_related_to_filtered_tests_only or len(self.filterHardware) > 0
        ):
            include_types = ["builds", "boots", "tests"]

        rows = get_tree_commit_history(
            commit_hash=commit_hash,
            origin=params.origin,
            git_url=params.git_url,
            git_branch=params.git_branch or git_branch,
            tree_name=tree_name,
            include_types=include_types,
        )

        if not rows:
            return create_api_error_response(
                error_message=ClientStrings.TREE_COMMITS_HISTORY_NOT_FOUND,
                status_code=HTTPStatus.OK,
            )

        self._process_rows(rows, params.types)

        # Format the results as JSON
        results = []

        for key, value in self.commit_hashes.items():
            results.append(
                {
                    "git_commit_hash": key,
                    "git_commit_name": value["commit_name"],
                    "git_commit_tags": value["commit_tags"],
                    "earliest_start_time": value["earliest_start_time"],
                    "builds": {
                        "FAIL": value["builds_count"]["fail"],
                        "ERROR": value["builds_count"]["error"],
                        "MISS": value["builds_count"]["miss"],
                        "PASS": value["builds_count"]["pass"],
                        "DONE": value["builds_count"]["done"],
                        "SKIP": value["builds_count"]["skip"],
                        "NULL": value["builds_count"]["null"],
                    },
                    "boots": {
                        "fail": value["boots_count"]["fail"],
                        "error": value["boots_count"]["error"],
                        "miss": value["boots_count"]["miss"],
                        "pass": value["boots_count"]["pass"],
                        "done": value["boots_count"]["done"],
                        "skip": value["boots_count"]["skip"],
                        "null": value["boots_count"]["null"],
                    },
                    "tests": {
                        "fail": value["tests_count"]["fail"],
                        "error": value["tests_count"]["error"],
                        "miss": value["tests_count"]["miss"],
                        "pass": value["tests_count"]["pass"],
                        "done": value["tests_count"]["done"],
                        "skip": value["tests_count"]["skip"],
                        "null": value["tests_count"]["null"],
                    },
                }
            )

        try:
            valid_response = TreeCommitsResponse(results)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump(by_alias=True))


class TreeCommitsHistoryDirect(BaseTreeCommitsHistory):
    @extend_schema(
        responses=TreeCommitsResponse,
        parameters=[
            COMMIT_HASH_PATH_PARAM,
            TREE_NAME_PATH_PARAM,
            GIT_BRANCH_PATH_PARAM,
            DirectTreeCommitsQueryParameters,
        ],
        methods=["GET"],
    )
    def get(
        self,
        request: HttpRequest,
        commit_hash: str,
        tree_name: str,
        git_branch: str,
    ) -> Response:
        return super().get(
            request=request,
            commit_hash=commit_hash,
            tree_name=tree_name,
            git_branch=git_branch,
        )


class TreeCommitsHistory(BaseTreeCommitsHistory):
    @extend_schema(
        responses=TreeCommitsResponse,
        parameters=[COMMIT_HASH_PATH_PARAM, TreeCommitsQueryParameters],
        methods=["GET"],
    )
    def get(self, request, commit_hash: str) -> Response:
        return super().get(request=request, commit_hash=commit_hash)
