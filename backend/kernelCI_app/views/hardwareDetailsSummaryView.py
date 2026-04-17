from collections import defaultdict
from datetime import datetime
from itertools import chain
from typing import Dict, Optional
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from http import HTTPStatus
import json
from kernelCI_app.constants.general import UNKNOWN_STRING
from kernelCI_app.helpers.issueExtras import parse_issue
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.filters import (
    FilterParams,
    is_filtered_out,
    is_valid_status,
)
from kernelCI_app.helpers.hardwareDetails import (
    generate_build_summary_typed,
    generate_test_summary_typed,
    unstable_parse_post_body,
)
from kernelCI_app.queries.hardware import (
    get_hardware_details_summary,
    get_hardware_trees_head_commits,
)
from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.commonDetails import (
    BuildArchitectures,
    BuildSummary,
    GlobalFilters,
    LocalFilters,
    Summary,
    TestArchSummaryItem,
    TestSummary,
)
from kernelCI_app.typeModels.commonOpenApiParameters import (
    HARDWARE_ID_PATH_PARAM,
)
from kernelCI_app.typeModels.hardwareDetails import (
    HardwareCommon,
    HardwareDetailsFilters,
    HardwareDetailsPostBody,
    HardwareDetailsSummaryResponse,
    HardwareTestLocalFilters,
    Tree,
)
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from kernelCI_app.constants.localization import ClientStrings


# disable django csrf protection https://docs.djangoproject.com/en/5.0/ref/csrf/
# that protection is recommended for ‘unsafe’ methods (POST, PUT, and DELETE)
# but we are using POST here just to follow the convention to use the request body
# also the csrf protection require the usage of cookies which is not currently
# supported in this project
@method_decorator(csrf_exempt, name="dispatch")
class HardwareDetailsSummary(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.origin: str = None
        self.start_datetime: datetime = None
        self.end_datetime: datetime = None
        self.selected_commits: Dict[str, str] = None
        self.filters: FilterParams = None

    def get_filter_type(
        self, is_build: bool, is_boot: bool, is_test: bool, **kwargs
    ) -> str:
        if is_build:
            return "build"
        if is_boot:
            return "boot"
        if is_test:
            return "test"
        raise ValueError("Invalid filter type")

    def get_summary_type(
        self, is_build: bool, is_boot: bool, is_test: bool, **kwargs
    ) -> str:
        if is_build:
            return "builds"
        if is_boot:
            return "boots"
        if is_test:
            return "tests"
        raise ValueError("Invalid summary type")

    def filter_instance(
        self,
        *,
        hardware_id: str,
        config: str,
        lab: str,
        compiler: str,
        architecture: str,
        compatibles: set[str],
        status: str,
        known_issues: set[str],
        is_build: bool,
        is_boot: bool,
        is_test: bool,
    ) -> bool:

        filters: FilterParams = self.filters
        filter_type = self.get_filter_type(is_build, is_boot, is_test)
        status_filter_map = {
            "build": filters.filterBuildStatus,
            "boot": filters.filterBootStatus,
            "test": filters.filterTestStatus,
        }
        if is_filtered_out(status, status_filter_map[filter_type]):
            return True
        if is_filtered_out(compiler, filters.filterCompiler):
            return True
        if is_filtered_out(config, filters.filterConfigs):
            return True
        if is_filtered_out(lab, filters.filter_labs):
            return True
        if is_filtered_out(architecture, filters.filterArchitecture):
            return True

        if filters.filterHardware and filters.filterHardware.isdisjoint(compatibles):
            return True

        filtered_issues = filters.filterIssues.get(filter_type, set())
        if filtered_issues and not known_issues.issubset(filtered_issues):
            return True

        return False

    def aggregate_summaries(
        self, summary: list[dict], hardware_id: str
    ) -> tuple[BuildSummary, TestSummary, TestSummary]:
        builds_summary = generate_build_summary_typed()
        tests_summary = generate_test_summary_typed()
        boots_summary = generate_test_summary_typed()

        tests_summary.platforms = {}
        boots_summary.platforms = {}

        # aggregation
        for instance in summary:
            status = instance["status"]
            count = instance["count"]
            incidents = instance["incidents_count"]
            known_issues = set(parse_issue(issue) for issue in instance["known_issues"])
            compatibles = set(instance["environment_compatible"] or [])
            config = instance["config_name"] or UNKNOWN_STRING
            origin = instance["origin"] or UNKNOWN_STRING
            lab = instance["lab"] or UNKNOWN_STRING
            platform = instance["platform"] or UNKNOWN_STRING
            is_build = instance["is_build"]
            is_test = instance["is_test"]
            is_boot = instance["is_boot"]
            (compiler, architecture) = [
                (val or UNKNOWN_STRING).strip(" []''")
                for val in (instance["compiler_arch"] or [None, None])
            ]

            status_count = StatusCount()
            status_count.increment(status, count)

            if self.filter_instance(
                hardware_id=hardware_id,
                config=config,
                lab=lab,
                compiler=compiler,
                architecture=architecture,
                compatibles=compatibles,
                status=status,
                known_issues=known_issues,
                is_build=is_build,
                is_boot=is_boot,
                is_test=is_test,
            ):
                continue

            if is_build:
                self.increment_build(
                    builds_summary=builds_summary,
                    status_count=status_count,
                    architecture=architecture,
                    config=config,
                    lab=lab,
                    origin=origin,
                    incidents=incidents,
                    compiler=compiler,
                )

            elif is_boot:
                self.increment_test(
                    tests_summary=boots_summary,
                    status_count=status_count,
                    config=config,
                    lab=lab,
                    origin=origin,
                    incidents=incidents,
                    architecture=architecture,
                    compiler=compiler,
                    platform=platform,
                )

            elif is_test:
                self.increment_test(
                    tests_summary=tests_summary,
                    status_count=status_count,
                    config=config,
                    lab=lab,
                    origin=origin,
                    incidents=incidents,
                    architecture=architecture,
                    compiler=compiler,
                    platform=platform,
                )

        # ensure uniqueness on architecture and compilers (maybe we could change data structures???)
        for summary in builds_summary.architectures.values():
            summary.compilers = sorted(set(summary.compilers or []))
        tests_summary_archs = defaultdict(StatusCount)
        for item in tests_summary.architectures:
            tests_summary_archs[(item.arch, item.compiler)] += item.status
        tests_summary.architectures = [
            TestArchSummaryItem(arch=arch, compiler=compiler, status=status)
            for (arch, compiler), status in tests_summary_archs.items()
        ]

        boots_summary_archs = defaultdict(StatusCount)
        for item in boots_summary.architectures:
            boots_summary_archs[(item.arch, item.compiler)] += item.status
        boots_summary.architectures = [
            TestArchSummaryItem(arch=arch, compiler=compiler, status=status)
            for (arch, compiler), status in boots_summary_archs.items()
        ]

        return (builds_summary, boots_summary, tests_summary)

    def increment_test(
        self,
        *,
        tests_summary: TestSummary,
        status_count: StatusCount,
        config: str,
        lab: str,
        origin: str,
        incidents: int,
        architecture: str,
        compiler: str,
        platform: str,
    ):
        if config not in tests_summary.configs:
            tests_summary.configs[config] = StatusCount()
        if lab not in tests_summary.labs:
            tests_summary.labs[lab] = StatusCount()
        if origin not in tests_summary.origins:
            tests_summary.origins[origin] = StatusCount()
        if platform not in tests_summary.platforms:
            tests_summary.platforms[platform] = StatusCount()

        tests_summary.status += status_count
        tests_summary.configs[config] += status_count
        tests_summary.labs[lab] += status_count
        tests_summary.architectures.append(
            TestArchSummaryItem(
                arch=architecture, compiler=compiler, status=status_count
            )
        )
        tests_summary.origins[origin] += status_count
        tests_summary.platforms[platform] += status_count
        if status_count.FAIL > 0:
            tests_summary.unknown_issues += status_count.FAIL - incidents

    def increment_build(
        self,
        *,
        builds_summary: BuildSummary,
        status_count: StatusCount,
        architecture: str,
        config: str,
        lab: str,
        origin: str,
        incidents: int,
        compiler: str,
    ):
        if architecture not in builds_summary.architectures:
            builds_summary.architectures[architecture] = BuildArchitectures(
                compilers=[]
            )
        if config not in builds_summary.configs:
            builds_summary.configs[config] = StatusCount()
        if lab not in builds_summary.labs:
            builds_summary.labs[lab] = StatusCount()
        if origin not in builds_summary.origins:
            builds_summary.origins[origin] = StatusCount()

        builds_summary.status += status_count
        builds_summary.configs[config] += status_count
        builds_summary.labs[lab] += status_count
        builds_summary.origins[origin] += status_count
        builds_summary.architectures[architecture] += status_count
        if compiler not in (builds_summary.architectures[architecture].compilers or []):
            builds_summary.architectures[architecture].compilers.append(compiler)
        if status_count.FAIL > 0:
            builds_summary.unknown_issues += status_count.FAIL - incidents

    def aggregate_common(
        self, summary: list[dict], hardware_id: str
    ) -> tuple[list[Tree], list[str]]:

        all_trees: dict[tuple, Tree] = dict()
        all_compatibles: set[str] = set()

        # aggregation
        for instance in summary:
            status = instance["status"]
            count = instance["count"]
            origin = instance["origin"] or UNKNOWN_STRING
            compatibles = set(instance["environment_compatible"] or [])
            tree_name = instance["tree_name"]
            git_repository_url = instance["git_repository_url"]
            git_repository_branch = instance["git_repository_branch"]
            git_commit_name = instance["git_commit_name"]
            git_commit_hash = instance["git_commit_hash"]
            git_commit_tags = instance["git_commit_tags"]

            status_count = StatusCount()
            status_count.increment(status, count)

            if not (tree_name, git_repository_url, git_repository_branch) in all_trees:
                all_trees[(tree_name, git_repository_url, git_repository_branch)] = (
                    Tree(
                        index="",  # if we dont mind to sort, we can just use len(all_trees)
                        tree_name=tree_name,
                        git_repository_branch=git_repository_branch,
                        git_repository_url=git_repository_url,
                        head_git_commit_hash=git_commit_hash,
                        head_git_commit_name=git_commit_name,
                        head_git_commit_tag=git_commit_tags,
                        origin=origin,
                        selected_commit_status={
                            "builds": StatusCount(),
                            "boots": StatusCount(),
                            "tests": StatusCount(),
                        },
                        is_selected=None,
                    )
                )
            row_type = self.get_summary_type(**instance)
            all_trees[
                (tree_name, git_repository_url, git_repository_branch)
            ].selected_commit_status[row_type] += status_count
            all_compatibles.update(compatibles or [])

        all_compatibles.discard(hardware_id)

        # not sure if it is worth sorting for index (but is also not slowing us down)
        sorted_trees = sorted(
            all_trees.values(),
            key=lambda t: (
                t.tree_name or "",
                t.git_repository_branch or "",
                t.head_git_commit_name or "",
            ),
        )
        for i, tree in enumerate(sorted_trees):
            tree.index = str(i)

        return sorted_trees, sorted(all_compatibles)

    def aggregate_filters(
        self,
        builds_summary: BuildSummary,
        boots_summary: TestSummary,
        tests_summary: TestSummary,
        hardware_id: str,
    ) -> tuple[
        GlobalFilters, LocalFilters, HardwareTestLocalFilters, HardwareTestLocalFilters
    ]:
        builds_configs = {*builds_summary.configs}
        boots_configs = {*boots_summary.configs}
        tests_configs = {*tests_summary.configs}
        all_config = {*builds_configs, *boots_configs, *tests_configs}

        builds_architectures = {*builds_summary.architectures}
        boots_architectures = {*[item.arch for item in boots_summary.architectures]}
        tests_architectures = {*[item.arch for item in tests_summary.architectures]}
        all_architectures = {
            *builds_architectures,
            *boots_architectures,
            *tests_architectures,
        }

        builds_compilers = {
            *[
                compiler
                for arch in builds_summary.architectures.values()
                for compiler in (arch.compilers or [])
            ]
        }
        boots_compilers = {*[item.compiler for item in boots_summary.architectures]}
        tests_compilers = {*[item.compiler for item in tests_summary.architectures]}
        all_compilers = {
            *builds_compilers,
            *boots_compilers,
            *tests_compilers,
        }

        builds_issues_version = {
            (item.id, item.version) for item in builds_summary.issues
        }
        boots_issues_version = {
            (item.id, item.version) for item in boots_summary.issues
        }
        tests_issues_version = {
            (item.id, item.version) for item in tests_summary.issues
        }

        builds_labs = {*builds_summary.labs}
        boots_labs = {*boots_summary.labs}
        tests_labs = {*tests_summary.labs}

        builds_origins = {*builds_summary.origins}
        boots_origins = {*boots_summary.origins}
        tests_origins = {*tests_summary.origins}

        boots_platforms = {*(boots_summary.platforms or [])}
        tests_platforms = {*(tests_summary.platforms or [])}

        return (
            GlobalFilters(
                configs=[*all_config],
                architectures=[*all_architectures],
                compilers=[*all_compilers],
            ),
            LocalFilters(
                issues=[*builds_issues_version],
                origins=[*builds_origins],
                has_unknown_issue=builds_summary.unknown_issues > 0,
                labs=[*builds_labs],
            ),
            HardwareTestLocalFilters(
                issues=[*boots_issues_version],
                origins=[*boots_origins],
                has_unknown_issue=boots_summary.unknown_issues > 0,
                platforms=[*boots_platforms],
                labs=[*boots_labs],
            ),
            HardwareTestLocalFilters(
                issues=[*tests_issues_version],
                origins=[*tests_origins],
                has_unknown_issue=tests_summary.unknown_issues > 0,
                platforms=[*tests_platforms],
                labs=[*tests_labs],
            ),
        )

    def valid_filter_status(self) -> bool:
        filters: FilterParams = self.filters
        return all(
            is_valid_status(filter_status)
            for filter_status in chain(
                filters.filterBuildStatus,
                filters.filterBootStatus,
                filters.filterTestStatus,
            )
        )

    def select_commits_hashes(
        self,
        tree_heads: list[(str, str)],
        selected_commits: Optional[dict[str, str]] = None,
    ):
        selected_commit_hashes = []
        if selected_commits:
            for idx, head in tree_heads:
                if idx in self.selected_commits:
                    selected_commit = self.selected_commits.get(idx, "head")
                    selected_commit_hashes.append(
                        head if selected_commit == "head" else selected_commit
                    )
        else:
            selected_commit_hashes = [head for (_, head) in tree_heads]
        return selected_commit_hashes

    def _validate_request(self, request) -> Response | None:
        try:
            unstable_parse_post_body(instance=self, request=request)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError:
            return Response(
                data={"error": ClientStrings.INVALID_JSON_BODY},
                status=HTTPStatus.BAD_REQUEST,
            )
        except (ValueError, TypeError) as e:
            return Response(
                data={
                    "error": ClientStrings.INVALID_TIMESTAMP,
                    "exception": str(e),
                },
                status=HTTPStatus.BAD_REQUEST,
            )

        if not self.valid_filter_status():
            return create_api_error_response(
                error_message=ClientStrings.INVALID_FILTERS,
                status_code=HTTPStatus.BAD_REQUEST,
            )
        return None

    def _get_error_response(
        self, message: str, status_code: int = HTTPStatus.OK
    ) -> Response:
        return create_api_error_response(
            error_message=message,
            status_code=status_code,
        )

    @extend_schema(
        parameters=[HARDWARE_ID_PATH_PARAM],
        responses=HardwareDetailsSummaryResponse,
        request=HardwareDetailsPostBody,
        methods=["POST"],
    )
    def post(self, request, hardware_id) -> Response:
        validation_error = self._validate_request(request)
        if validation_error:
            return validation_error

        try:
            tree_heads = get_hardware_trees_head_commits(
                hardware_id=hardware_id,
                origin=self.origin,
                start_datetime=self.start_datetime,
                end_datetime=self.end_datetime,
            )

            if not tree_heads:
                return self._get_error_response(ClientStrings.HARDWARE_NO_COMMITS)

            filters: FilterParams = self.filters

            selected_commit_hashes = self.select_commits_hashes(
                tree_heads, self.selected_commits
            )

            summary: list[dict] = get_hardware_details_summary(
                hardware_id=hardware_id,
                origin=self.origin,
                commit_hashes=selected_commit_hashes,
                start_datetime=self.start_datetime,
                end_datetime=self.end_datetime,
                builds_duration=(
                    filters.filterBuildDurationMin,
                    filters.filterBuildDurationMax,
                ),
                boots_duration=(
                    filters.filterBootDurationMin,
                    filters.filterBootDurationMax,
                ),
                tests_duration=(
                    filters.filterTestDurationMin,
                    filters.filterTestDurationMax,
                ),
            )

            if not summary:
                return self._get_error_response(ClientStrings.HARDWARE_NOT_FOUND)

            # TODO: necessary due to the fact we return filter info,
            # a dedicated endpoint for filters is important
            if filters.filters or self.selected_commits:
                head_commit_hashes = self.select_commits_hashes(tree_heads)
                unfiltered_summary = get_hardware_details_summary(
                    hardware_id=hardware_id,
                    origin=self.origin,
                    commit_hashes=head_commit_hashes,
                    start_datetime=self.start_datetime,
                    end_datetime=self.end_datetime,
                )
            else:
                unfiltered_summary = summary

            builds_summary, boots_summary, tests_summary = self.aggregate_summaries(
                summary, hardware_id
            )
            all_trees, all_compatibles = self.aggregate_common(
                unfiltered_summary, hardware_id
            )
            all_filters, builds_filters, boots_filters, tests_filters = (
                self.aggregate_filters(
                    *self.aggregate_summaries(unfiltered_summary, hardware_id),
                    hardware_id,
                )
            )

            summary = Summary(
                builds=builds_summary, boots=boots_summary, tests=tests_summary
            )
            commons = HardwareCommon(trees=all_trees, compatibles=all_compatibles)
            filters = HardwareDetailsFilters(
                all=all_filters,
                builds=builds_filters,
                boots=boots_filters,
                tests=tests_filters,
            )

            valid_response = HardwareDetailsSummaryResponse(
                summary=summary, filters=filters, common=commons
            )

            return Response(valid_response.model_dump())
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)
