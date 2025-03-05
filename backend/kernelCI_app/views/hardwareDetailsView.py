from collections import defaultdict
from datetime import datetime
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from http import HTTPStatus
from kernelCI_app.helpers.commonDetails import PossibleTabs
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.helpers.hardwareDetails import (
    assign_default_record_values,
    decide_if_is_build_in_filter,
    decide_if_is_full_record_filtered_out,
    decide_if_is_test_in_filter,
    generate_test_dict,
    generate_tree_status_summary_dict,
    get_build_typed,
    get_filter_options,
    get_processed_issue_key,
    get_trees_with_selected_commit,
    get_validated_current_tree,
    handle_build,
    handle_tree_status_summary,
    is_issue_processed,
    is_test_processed,
    mutate_properties_to_list,
    process_issue,
    set_trees_status_summary,
    unstable_parse_post_body,
    handle_test_history,
)
from kernelCI_app.queries.hardware import (
    get_hardware_details_data,
    get_hardware_trees_data,
)
from kernelCI_app.typeModels.commonDetails import (
    BuildSummary,
    GlobalFilters,
    LocalFilters,
    Summary,
    TestSummary,
)
from kernelCI_app.typeModels.hardwareDetails import (
    HardwareCommon,
    HardwareDetailsFilters,
    HardwareDetailsFullResponse,
    HardwareDetailsPostBody,
    HardwareTestLocalFilters,
    PossibleTestType,
    Tree,
)
from kernelCI_app.utils import is_boot
from kernelCI_app.viewCommon import create_details_build_summary
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from typing import Dict, List, Set


# disable django csrf protection https://docs.djangoproject.com/en/5.0/ref/csrf/
# that protection is recommended for ‘unsafe’ methods (POST, PUT, and DELETE)
# but we are using POST here just to follow the convention to use the request body
# also the csrf protection require the usage of cookies which is not currently
# supported in this project
@method_decorator(csrf_exempt, name="dispatch")
class HardwareDetails(APIView):
    required_params_get = ["origin"]

    def __init__(self):
        self.origin: str = None
        self.start_datetime: datetime = None
        self.end_datetime: datetime = None
        self.selected_commits: Dict[str, str] = None

        self.filters: FilterParams = None

        self.processed_builds = set()
        self.processed_tests = set()

        self.processed_issues: Dict[str, Set[str]] = {
            "build": set(),
            "boot": set(),
            "test": set(),
        }

        self.processed_compatibles: Set[str] = set()

        self.builds = {
            "items": [],
            "issues": {},
            "failedWithUnknownIssues": 0,
        }
        self.boots = generate_test_dict()
        self.tests = generate_test_dict()

        self.unfiltered_build_issues = set()
        self.unfiltered_boot_issues = set()
        self.unfiltered_test_issues = set()

        self.unfiltered_boot_platforms = set()
        self.unfiltered_test_platforms = set()

        self.global_configs = set()
        self.global_architectures = set()
        self.global_compilers = set()

        self.tree_status_summary = defaultdict(generate_tree_status_summary_dict)

    def _process_test(self, record: Dict) -> None:
        is_record_boot = is_boot(record["path"])
        test_type_key: PossibleTestType = "boot" if is_record_boot else "test"
        task = self.boots if is_record_boot else self.tests

        is_test_processed_result = is_test_processed(
            record=record, processed_tests=self.processed_tests
        )
        is_issue_processed_result = is_issue_processed(
            record=record, processed_issues=self.processed_issues[test_type_key]
        )
        should_process_test = decide_if_is_test_in_filter(
            instance=self,
            test_type=test_type_key,
            record=record,
            processed_tests=self.processed_tests,
        )

        if (
            should_process_test
            and not is_issue_processed_result
            and is_test_processed_result
        ):
            process_issue(
                record=record,
                task_issues_dict=task,
                issue_from="test",
            )
            processed_issue_key = get_processed_issue_key(record=record)
            self.processed_issues[test_type_key].add(processed_issue_key)

        if should_process_test and not is_test_processed_result:
            self.processed_tests.add(record["id"])
            test_or_boot_history = (
                self.boots["history"] if is_record_boot else self.tests["history"]
            )
            handle_test_history(
                record=record,
                task=test_or_boot_history,
            )

    def _process_build(self, record: Dict, tree_index: int) -> None:
        build = get_build_typed(record, tree_index)
        build_id = record["build_id"]

        should_process_build = decide_if_is_build_in_filter(
            instance=self,
            build=build,
            processed_builds=self.processed_builds,
            incident_test_id=record["incidents__test_id"],
        )

        self.processed_builds.add(build_id)
        if should_process_build:
            handle_build(instance=self, record=record, build=build)

    def _sanitize_records(
        self, records, trees: List[Tree], is_all_selected: bool
    ) -> None:
        for record in records:
            current_tree = get_validated_current_tree(
                record=record, selected_trees=trees
            )
            if current_tree is None:
                continue

            assign_default_record_values(record)

            if record["environment_compatible"] is not None:
                self.processed_compatibles.update(record["environment_compatible"])

            tree_index = current_tree.index

            handle_tree_status_summary(
                record=record,
                tree_status_summary=self.tree_status_summary,
                tree_index=tree_index,
                processed_builds=self.processed_builds,
            )

            is_record_filtered_out = decide_if_is_full_record_filtered_out(
                instance=self,
                record=record,
                current_tree=current_tree,
                is_all_selected=is_all_selected,
            )
            if is_record_filtered_out:
                self.processed_builds.add(record["build_id"])
                continue

            self._process_test(record=record)

            self._process_build(record, tree_index)

    def _format_processing_for_response(self):
        mutate_properties_to_list(self.builds, ["issues"])
        mutate_properties_to_list(
            self.tests, ["issues", "platformsFailing", "archSummary"]
        )
        mutate_properties_to_list(
            self.boots, ["issues", "platformsFailing", "archSummary"]
        )

    # Using post to receive a body request
    @extend_schema(
        responses=HardwareDetailsFullResponse,
        request=HardwareDetailsPostBody,
        methods=["POST"],
    )
    def post(self, request, hardware_id):
        try:
            unstable_parse_post_body(instance=self, request=request)
        except ValidationError as e:
            return Response(data={"error": e.json()}, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError:
            return Response(
                data={
                    "error": "Invalid body, request body must be a valid json string"
                },
                status=HTTPStatus.BAD_REQUEST,
            )
        except (ValueError, TypeError):
            return Response(
                data={
                    "error": "startTimeStamp and endTimeStamp must be a Unix Timestamp"
                },
                status=HTTPStatus.BAD_REQUEST,
            )

        trees = get_hardware_trees_data(
            hardware_id=hardware_id,
            origin=self.origin,
            selected_commits=self.selected_commits,
            start_datetime=self.start_datetime,
            end_datetime=self.end_datetime,
        )

        if len(trees) == 0:
            return create_api_error_response(
                error_message="This hardware isn't associated with any commit",
                status_code=HTTPStatus.OK,
            )

        trees_with_selected_commits = get_trees_with_selected_commit(
            trees=trees, selected_commits=self.selected_commits
        )

        records = get_hardware_details_data(
            hardware_id=hardware_id,
            origin=self.origin,
            trees_with_selected_commits=trees_with_selected_commits,
            start_datetime=self.start_datetime,
            end_datetime=self.end_datetime,
        )

        # Temporary during schema transition
        if records is None:
            message = (
                "This error was probably caused because the server was using"
                "an old version of the database. Please try requesting again"
            )
            return create_api_error_response(
                error_message=message,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        if len(records) == 0:
            return Response(data={"error": "Hardware not found"}, status=HTTPStatus.OK)

        is_all_selected = len(self.selected_commits) == 0

        self._sanitize_records(records, trees_with_selected_commits, is_all_selected)

        self.builds["summary"] = create_details_build_summary(self.builds["items"])
        self._format_processing_for_response()

        self.unfiltered_uncategorized_issue_flags: Dict[PossibleTabs, bool] = {
            "build": False,
            "boot": False,
            "test": False,
        }

        get_filter_options(
            instance=self,
            records=records,
            selected_trees=trees_with_selected_commits,
            is_all_selected=is_all_selected,
        )

        set_trees_status_summary(
            trees=trees, tree_status_summary=self.tree_status_summary
        )

        try:
            valid_response = HardwareDetailsFullResponse(
                builds=self.builds["items"],
                boots=self.boots["history"],
                tests=self.tests["history"],
                summary=Summary(
                    builds=BuildSummary(
                        status=self.builds["summary"]["builds"],
                        architectures=self.builds["summary"]["architectures"],
                        configs=self.builds["summary"]["configs"],
                        issues=self.builds["issues"],
                        unknown_issues=self.builds["failedWithUnknownIssues"],
                    ),
                    boots=TestSummary(
                        status=self.boots["statusSummary"],
                        architectures=self.boots["archSummary"],
                        configs=self.boots["configs"],
                        issues=self.boots["issues"],
                        unknown_issues=self.boots["failedWithUnknownIssues"],
                        platforms=self.boots["platforms"],
                        fail_reasons=self.boots["failReasons"],
                        failed_platforms=list(self.boots["platformsFailing"]),
                    ),
                    tests=TestSummary(
                        status=self.tests["statusSummary"],
                        architectures=self.tests["archSummary"],
                        configs=self.tests["configs"],
                        issues=self.tests["issues"],
                        unknown_issues=self.tests["failedWithUnknownIssues"],
                        platforms=self.tests["platforms"],
                        fail_reasons=self.tests["failReasons"],
                        failed_platforms=list(self.tests["platformsFailing"]),
                    ),
                ),
                filters=HardwareDetailsFilters(
                    all=GlobalFilters(
                        configs=self.global_configs,
                        architectures=self.global_architectures,
                        compilers=self.global_compilers,
                    ),
                    builds=LocalFilters(
                        issues=list(self.unfiltered_build_issues),
                        has_unknown_issue=self.unfiltered_uncategorized_issue_flags[
                            "build"
                        ],
                    ),
                    boots=HardwareTestLocalFilters(
                        issues=list(self.unfiltered_boot_issues),
                        platforms=list(self.unfiltered_boot_platforms),
                        has_unknown_issue=self.unfiltered_uncategorized_issue_flags[
                            "boot"
                        ],
                    ),
                    tests=HardwareTestLocalFilters(
                        issues=list(self.unfiltered_test_issues),
                        platforms=list(self.unfiltered_test_platforms),
                        has_unknown_issue=self.unfiltered_uncategorized_issue_flags[
                            "test"
                        ],
                    ),
                ),
                common=HardwareCommon(
                    trees=trees,
                    compatibles=list(self.processed_compatibles - {hardware_id}),
                ),
            )
        except ValidationError as e:
            return Response(data=e.errors(), status=HTTPStatus.BAD_REQUEST)

        return Response(valid_response.model_dump())
