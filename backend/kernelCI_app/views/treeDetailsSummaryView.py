from typing import Any, Dict
from pydantic import ValidationError
from rest_framework.response import Response
from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.helpers.commonDetails import PossibleTabs
from kernelCI_app.helpers.discordWebhook import send_discord_notification
from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.helpers.logger import create_endpoint_notification
from kernelCI_app.helpers.treeDetails import (
    call_based_on_compatible_and_misc_platform,
    decide_if_is_boot_filtered_out,
    decide_if_is_build_filtered_out,
    decide_if_is_full_row_filtered_out,
    decide_if_is_test_filtered_out,
    get_build,
    get_current_row_data,
    process_tree_url,
    process_boots_summary,
    process_builds_issue,
    process_test_summary,
    process_tests_issue,
    process_filters,
)
from kernelCI_app.queries.tree import get_tree_details_data
from kernelCI_app.typeModels.commonDetails import (
    BaseBuildSummary,
    BuildSummary,
    DetailsFilters,
    GlobalFilters,
    LocalFilters,
    Summary,
    TestSummary,
)
from kernelCI_app.typeModels.issues import IssueDict
from kernelCI_app.typeModels.treeDetails import (
    SummaryResponse,
    TreeCommon,
    TreeQueryParameters,
)
from kernelCI_app.utils import convert_issues_dict_to_list_typed, is_boot

from collections import defaultdict

from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from kernelCI_app.viewCommon import create_details_build_summary
from kernelCI_app.helpers.errorHandling import create_api_error_response
from http import HTTPStatus
from kernelCI_app.constants.general import MAESTRO_DUMMY_BUILD_PREFIX


class TreeDetailsSummary(APIView):
    def __init__(self):
        self.processedTests = set()
        self.filters = None

        self.testStatusSummary = {}
        self.test_configs = {}
        self.testPlatformsWithErrors = set()
        self.testFailReasons = {}
        self.test_arch_summary = {}
        self.testIssues = []
        self.testIssuesTable = {}
        self.testEnvironmentCompatible = defaultdict(lambda: defaultdict(int))
        self.testEnvironmentMisc = defaultdict(lambda: defaultdict(int))
        self.bootStatusSummary = {}
        self.bootConfigs = {}
        self.bootPlatformsFailing = set()
        self.bootFailReasons = {}
        self.bootArchSummary = {}
        self.bootIssues = []
        self.bootsIssuesTable = {}
        self.bootEnvironmentCompatible = defaultdict(lambda: defaultdict(int))
        self.bootEnvironmentMisc = defaultdict(lambda: defaultdict(int))
        self.hardwareUsed = set()
        self.failed_tests_with_unknown_issues = 0
        self.failed_boots_with_unknown_issues = 0
        self.builds = []
        self.processed_builds = set()
        self.build_issues = []
        self.failed_builds_with_unknown_issues = 0
        self.tree_url = ""
        self.git_commit_tags = []

        self.build_issues_dict: IssueDict = {}
        self.boot_issues_dict: IssueDict = {}
        self.test_issues_dict: IssueDict = {}

        self.global_configs = set()
        self.global_architectures = set()
        self.global_compilers = set()
        self.unfiltered_test_issues = set()
        self.unfiltered_boot_issues = set()
        self.unfiltered_build_issues = set()
        self.unfiltered_uncategorized_issue_flags: Dict[PossibleTabs, bool] = {
            "build": False,
            "boot": False,
            "test": False,
        }

        self.unfiltered_origins: dict[PossibleTabs, set[str]] = {
            "build": set(),
            "boot": set(),
            "test": set(),
        }

        # TODO: move to a BuildSummary model and combine with the other fields above
        self.base_build_summary = BaseBuildSummary()

        # TODO: move to a TestSummary model and combine with the other fields above
        self.test_summary: dict[str, Any] = {"origins": {}}

        self.boot_summary: dict[str, Any] = {"origins": {}}

    def _process_boots_test(self, row_data):
        test_id = row_data["test_id"]

        if decide_if_is_boot_filtered_out(self, row_data):
            return

        process_tests_issue(instance=self, row_data=row_data, is_boot=True)

        if test_id in self.processedTests:
            return
        self.processedTests.add(test_id)
        process_boots_summary(self, row_data)

    def _process_non_boots_test(self, row_data):
        test_id = row_data["test_id"]

        if decide_if_is_test_filtered_out(self, row_data):
            return

        process_tests_issue(instance=self, row_data=row_data)

        if test_id in self.processedTests:
            return

        self.processedTests.add(test_id)
        process_test_summary(self, row_data)

    def _process_builds(self, row_data):
        build_id = row_data["build_id"]

        if decide_if_is_build_filtered_out(self, row_data):
            return

        process_builds_issue(instance=self, row_data=row_data)

        if build_id in self.processed_builds:
            return

        self.processed_builds.add(build_id)

        self.builds.append(get_build(row_data))

    def _sanitize_rows(self, rows):
        first_iteration = True
        for row in rows:
            row_data = get_current_row_data(row)
            if first_iteration is True:
                self.git_commit_tags = row_data["checkout_git_commit_tags"]
                first_iteration = False

            call_based_on_compatible_and_misc_platform(row_data, self.hardwareUsed.add)

            process_tree_url(self, row_data)
            process_filters(self, row_data)

            is_record_filter_out = decide_if_is_full_row_filtered_out(self, row_data)

            if is_record_filter_out:
                continue

            if row_data["build_id"] is not None and not row_data["build_id"].startswith(
                MAESTRO_DUMMY_BUILD_PREFIX
            ):
                self._process_builds(row_data)

            if row_data["test_id"] is None:
                continue

            if is_boot(row_data["test_path"]):
                self._process_boots_test(row_data)
            else:
                self._process_non_boots_test(row_data)

        self.base_build_summary = create_details_build_summary(self.builds)
        self.build_issues = convert_issues_dict_to_list_typed(
            issues_dict=self.build_issues_dict
        )
        self.bootIssues = convert_issues_dict_to_list_typed(
            issues_dict=self.boot_issues_dict
        )
        self.testIssues = convert_issues_dict_to_list_typed(
            issues_dict=self.test_issues_dict
        )

    @extend_schema(
        responses=SummaryResponse,
        parameters=[TreeQueryParameters],
        methods=["GET"],
    )
    def get(self, request, commit_hash: str | None) -> Response:
        origin_param = request.GET.get("origin")
        git_url_param = request.GET.get("git_url")
        git_branch_param = request.GET.get("git_branch")

        rows = get_tree_details_data(
            origin_param, git_url_param, git_branch_param, commit_hash
        )

        if len(rows) == 0:
            return create_api_error_response(
                error_message=ClientStrings.TREE_NOT_FOUND,
                status_code=HTTPStatus.OK,
            )

        if len(rows) == 1:
            row_data = get_current_row_data(rows[0])
            if row_data["build_id"] is None:
                notification = create_endpoint_notification(
                    message="Found checkout without builds",
                    request=request,
                )
                send_discord_notification(content=notification)
                return create_api_error_response(
                    error_message=ClientStrings.TREE_BUILDS_NOT_FOUND,
                    status_code=HTTPStatus.OK,
                )

        self.filters = FilterParams(request)

        self._sanitize_rows(rows)

        try:
            valid_response = SummaryResponse(
                common=TreeCommon(
                    tree_url=self.tree_url,
                    hardware=list(self.hardwareUsed),
                    git_commit_tags=self.git_commit_tags,
                ),
                summary=Summary(
                    builds=BuildSummary(
                        status=self.base_build_summary.status,
                        origins=self.base_build_summary.origins,
                        architectures=self.base_build_summary.architectures,
                        configs=self.base_build_summary.configs,
                        issues=self.build_issues,
                        unknown_issues=self.failed_builds_with_unknown_issues,
                    ),
                    boots=TestSummary(
                        status=self.bootStatusSummary,
                        origins=self.boot_summary["origins"],
                        architectures=list(self.bootArchSummary.values()),
                        configs=self.bootConfigs,
                        issues=self.bootIssues,
                        unknown_issues=self.failed_boots_with_unknown_issues,
                        environment_compatible=self.bootEnvironmentCompatible,
                        environment_misc=self.bootEnvironmentMisc,
                        fail_reasons=self.bootFailReasons,
                        failed_platforms=list(self.bootPlatformsFailing),
                    ),
                    tests=TestSummary(
                        status=self.testStatusSummary,
                        origins=self.test_summary["origins"],
                        architectures=list(self.test_arch_summary.values()),
                        configs=self.test_configs,
                        issues=self.testIssues,
                        unknown_issues=self.failed_tests_with_unknown_issues,
                        environment_compatible=self.testEnvironmentCompatible,
                        environment_misc=self.testEnvironmentMisc,
                        fail_reasons=self.testFailReasons,
                        failed_platforms=list(self.testPlatformsWithErrors),
                    ),
                ),
                filters=DetailsFilters(
                    all=GlobalFilters(
                        configs=list(self.global_configs),
                        architectures=list(self.global_architectures),
                        compilers=list(self.global_compilers),
                    ),
                    builds=LocalFilters(
                        issues=list(self.unfiltered_build_issues),
                        has_unknown_issue=self.unfiltered_uncategorized_issue_flags[
                            "build"
                        ],
                        origins=sorted(self.unfiltered_origins["build"]),
                    ),
                    boots=LocalFilters(
                        issues=list(self.unfiltered_boot_issues),
                        has_unknown_issue=self.unfiltered_uncategorized_issue_flags[
                            "boot"
                        ],
                        origins=sorted(self.unfiltered_origins["boot"]),
                    ),
                    tests=LocalFilters(
                        issues=list(self.unfiltered_test_issues),
                        has_unknown_issue=self.unfiltered_uncategorized_issue_flags[
                            "test"
                        ],
                        origins=sorted(self.unfiltered_origins["test"]),
                    ),
                ),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
