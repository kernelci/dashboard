from typing import Any, Dict, Optional
from django.http import HttpRequest
from kernelCI_app.helpers.hardwareDetails import generate_test_summary_typed
from pydantic import ValidationError
from rest_framework.response import Response
from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.helpers.commonDetails import PossibleTabs
from kernelCI_app.helpers.discordWebhook import send_discord_notification
from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.helpers.logger import create_endpoint_notification
from kernelCI_app.helpers.treeDetails import (
    decide_if_is_build_filtered_out,
    get_build,
    process_builds_issue,
    process_tree_url,
)
from kernelCI_app.helpers.treeDetailsRollup import (
    normalize_build_dict,
    process_build_filters,
    process_rollup_filters,
    process_rollup_issues,
    process_rollup_summary,
    rollup_test_or_boot_filtered_out,
)
from kernelCI_app.queries.tree import get_tree_details_builds, get_tree_details_rollup
from kernelCI_app.typeModels.commonDetails import (
    BaseBuildSummary,
    BuildSummary,
    DetailsFilters,
    GlobalFilters,
    LocalFilters,
    Summary,
    TestSummary,
)
from kernelCI_app.typeModels.commonOpenApiParameters import (
    COMMIT_HASH_PATH_PARAM,
    GIT_BRANCH_PATH_PARAM,
    TREE_NAME_PATH_PARAM,
)
from kernelCI_app.typeModels.issues import IssueDict
from kernelCI_app.typeModels.treeDetails import (
    DirectTreeQueryParameters,
    SummaryResponse,
    TreeCommon,
    TreeQueryParameters,
)
from kernelCI_app.utils import convert_issues_dict_to_list_typed

from collections import defaultdict

from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from kernelCI_app.viewCommon import create_details_build_summary
from kernelCI_app.helpers.errorHandling import create_api_error_response
from http import HTTPStatus
from kernelCI_app.constants.general import (
    DEFAULT_ORIGIN,
    MAESTRO_DUMMY_BUILD_PREFIX,
    UNKNOWN_STRING,
)


class BaseTreeDetailsSummary(APIView):
    def __init__(self):
        self.filters = None

        self.testStatusSummary = {}
        self.test_configs = {}
        self.testPlatformsWithErrors = set()
        self.testFailReasons = {}
        self.test_arch_summary = {}
        self.testIssues = []
        self.testEnvironmentCompatible = defaultdict(lambda: defaultdict(int))
        self.testEnvironmentMisc = defaultdict(lambda: defaultdict(int))
        self.bootStatusSummary = {}
        self.bootConfigs = {}
        self.bootPlatformsFailing = set()
        self.bootFailReasons = {}
        self.bootArchSummary = {}
        self.bootIssues = []
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

        self.unfiltered_labs: dict[PossibleTabs, set[str]] = {
            "build": set(),
            "boot": set(),
            "test": set(),
        }

        # TODO: move to a BuildSummary model and combine with the other fields above
        self.base_build_summary = BaseBuildSummary(labs={})

        # TODO: move to a TestSummary model and combine with the other fields above
        self.test_summary: dict[str, Any] = {"origins": {}}
        self.test_summary_typed: TestSummary = generate_test_summary_typed()

        self.boot_summary: dict[str, Any] = {"origins": {}}
        self.boot_summary_typed: TestSummary = generate_test_summary_typed()

    def _process_builds(self, row_data):
        build_id = row_data["build_id"]

        if decide_if_is_build_filtered_out(self, row_data):
            return

        process_builds_issue(instance=self, row_data=row_data)

        if build_id in self.processed_builds:
            return

        self.processed_builds.add(build_id)
        self.builds.append(get_build(row_data))

    def _sanitize_builds_rows(self, builds_rows: list[dict]) -> None:
        for row_dict in builds_rows:
            row_data = normalize_build_dict(row_dict)

            if not self.git_commit_tags:
                self.git_commit_tags = row_data.get("checkout_git_commit_tags", [])

            process_tree_url(self, row_data)
            process_build_filters(self, row_data)

            if self.filters.is_record_filtered_out(
                architecture=row_data["build_architecture"],
                compiler=row_data["build_compiler"],
                config_name=row_data["build_config_name"],
            ):
                continue

            build_id = row_data.get("build_id")
            if build_id is not None and not build_id.startswith(
                MAESTRO_DUMMY_BUILD_PREFIX
            ):
                self._process_builds(row_data)

        self.base_build_summary = create_details_build_summary(self.builds)
        self.build_issues = convert_issues_dict_to_list_typed(
            issues_dict=self.build_issues_dict
        )

    def _sanitize_rollup_rows(self, rollup_rows: list[dict]) -> None:
        for row_dict in rollup_rows:
            self.hardwareUsed.add(row_dict["hardware_key"])

            process_rollup_filters(self, row_dict)

            if self.filters.is_record_filtered_out(
                hardwares=[row_dict["hardware_key"]],
                architecture=row_dict["build_architecture"],
                compiler=row_dict["build_compiler"],
                config_name=row_dict["build_config_name"],
                lab=row_dict.get("test_lab", UNKNOWN_STRING),
            ):
                continue

            is_boot_row = row_dict["is_boot"]

            if rollup_test_or_boot_filtered_out(
                self, row_dict=row_dict, is_boot_row=is_boot_row
            ):
                continue

            process_rollup_issues(self, row_dict=row_dict, is_boot_row=is_boot_row)
            process_rollup_summary(self, row_dict=row_dict, is_boot_row=is_boot_row)

        self.bootIssues = convert_issues_dict_to_list_typed(
            issues_dict=self.boot_issues_dict
        )
        self.testIssues = convert_issues_dict_to_list_typed(
            issues_dict=self.test_issues_dict
        )

    def get(
        self,
        request: HttpRequest,
        commit_hash: Optional[str],
        tree_name: Optional[str] = None,
        git_branch: Optional[str] = None,
    ) -> Response:
        origin_param = request.GET.get("origin", DEFAULT_ORIGIN)
        git_url_param = request.GET.get("git_url")
        git_branch_param = request.GET.get("git_branch", git_branch)

        query_params = {
            "origin_param": origin_param,
            "git_url_param": git_url_param,
            "git_branch_param": git_branch_param,
            "commit_hash": commit_hash,
            "tree_name": tree_name,
        }

        builds_rows = get_tree_details_builds(**query_params)
        rollup_rows = get_tree_details_rollup(**query_params)

        if not builds_rows and not rollup_rows:
            return create_api_error_response(
                error_message=ClientStrings.TREE_NO_RESULTS,
                status_code=HTTPStatus.OK,
            )

        if not builds_rows:
            notification = create_endpoint_notification(
                message="Found checkout without builds",
                request=request,
            )
            send_discord_notification(content=notification)
            return create_api_error_response(
                error_message=ClientStrings.TREE_BUILDS_NO_RESULTS,
                status_code=HTTPStatus.OK,
            )

        self.filters = FilterParams(request)

        self._sanitize_builds_rows(builds_rows)
        self._sanitize_rollup_rows(rollup_rows or [])

        try:
            valid_response = SummaryResponse(
                common=TreeCommon(
                    tree_url=self.tree_url,
                    hardware=list(self.hardwareUsed),
                    git_commit_tags=self.git_commit_tags,
                ),
                summary=Summary(
                    builds=BuildSummary(
                        **self.base_build_summary.model_dump(),
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
                        labs=self.boot_summary_typed.labs,
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
                        labs=self.test_summary_typed.labs,
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
                        labs=self.unfiltered_labs["build"],
                    ),
                    boots=LocalFilters(
                        issues=list(self.unfiltered_boot_issues),
                        has_unknown_issue=self.unfiltered_uncategorized_issue_flags[
                            "boot"
                        ],
                        origins=sorted(self.unfiltered_origins["boot"]),
                        labs=self.unfiltered_labs["boot"],
                    ),
                    tests=LocalFilters(
                        issues=list(self.unfiltered_test_issues),
                        has_unknown_issue=self.unfiltered_uncategorized_issue_flags[
                            "test"
                        ],
                        origins=sorted(self.unfiltered_origins["test"]),
                        labs=self.unfiltered_labs["test"],
                    ),
                ),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())


class TreeDetailsSummaryDirect(BaseTreeDetailsSummary):
    @extend_schema(
        responses=SummaryResponse,
        parameters=[
            COMMIT_HASH_PATH_PARAM,
            TREE_NAME_PATH_PARAM,
            GIT_BRANCH_PATH_PARAM,
            DirectTreeQueryParameters,
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


class TreeDetailsSummary(BaseTreeDetailsSummary):
    @extend_schema(
        responses=SummaryResponse,
        parameters=[COMMIT_HASH_PATH_PARAM, TreeQueryParameters],
        methods=["GET"],
    )
    def get(self, request, commit_hash: str) -> Response:
        return super().get(request=request, commit_hash=commit_hash)
