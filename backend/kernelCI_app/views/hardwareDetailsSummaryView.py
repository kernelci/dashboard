from collections import defaultdict
from datetime import datetime
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from http import HTTPStatus
import json
from kernelCI_app.helpers.commonDetails import PossibleTabs
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.hardwareDetails import (
    assign_default_record_values,
    decide_if_is_build_in_filter,
    decide_if_is_full_record_filtered_out,
    decide_if_is_test_in_filter,
    generate_build_summary_typed,
    generate_test_summary_typed,
    generate_tree_status_summary_dict,
    get_build_typed,
    get_filter_options,
    get_processed_issue_key,
    get_trees_with_selected_commit,
    get_validated_current_tree,
    handle_build_summary,
    handle_test_summary,
    handle_tree_status_summary,
    is_issue_processed,
    is_test_processed,
    process_issue,
    set_trees_status_summary,
    format_issue_summary_for_response,
    unstable_parse_post_body,
)
from kernelCI_app.queries.hardware import (
    get_hardware_details_data,
    get_hardware_trees_data,
)
from kernelCI_app.typeModels.commonDetails import (
    GlobalFilters,
    LocalFilters,
    Summary,
    TestArchSummaryItem,
)
from kernelCI_app.typeModels.hardwareDetails import (
    HardwareCommon,
    HardwareDetailsFilters,
    HardwareDetailsPostBody,
    HardwareDetailsSummaryResponse,
    HardwareTestLocalFilters,
    PossibleTestType,
    Tree,
)
from kernelCI_app.utils import is_boot
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
class HardwareDetailsSummary(APIView):
    def __init__(self):
        self.origin: str = None
        self.start_datetime: datetime = None
        self.end_datetime: datetime = None
        self.selected_commits: Dict[str, str] = None

        self.processed_builds = set()
        self.processed_tests = set()

        self.processed_issues: Dict[str, Set[str]] = {
            "build": set(),
            "boot": set(),
            "test": set(),
        }

        self.processed_compatibles: Set[str] = set()

        self.issue_dicts = {
            "build": {
                "issues": {},
                "failedWithUnknownIssues": 0,
            },
            "boot": {
                "issues": {},
                "failedWithUnknownIssues": 0,
            },
            "test": {
                "issues": {},
                "failedWithUnknownIssues": 0,
            },
        }

        self.processed_architectures: Dict[str, Dict[str, TestArchSummaryItem]] = {
            "build": {},
            "boot": {},
            "test": {},
        }

        self.unfiltered_build_issues = set()
        self.unfiltered_boot_issues = set()
        self.unfiltered_test_issues = set()
        self.unfiltered_uncategorized_issue_flags: Dict[PossibleTabs, bool] = {
            "build": False,
            "boot": False,
            "test": False,
        }

        self.unfiltered_boot_platforms = set()
        self.unfiltered_test_platforms = set()

        self.global_configs = set()
        self.global_architectures = set()
        self.global_compilers = set()

        self.builds_summary = generate_build_summary_typed()
        self.boots_summary = generate_test_summary_typed()
        self.tests_summary = generate_test_summary_typed()

        self.tree_status_summary = defaultdict(generate_tree_status_summary_dict)
        self.compatibles: List[str] = []

        self.unfiltered_origins: dict[str, set[str]] = {
            "build": set(),
            "boot": set(),
            "test": set(),
        }

    def _process_test(self, record: Dict) -> None:
        is_record_boot = is_boot(record["path"])
        test_type_key: PossibleTestType = "boot" if is_record_boot else "test"
        task = self.boots_summary if is_record_boot else self.tests_summary

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
                task_issues_dict=self.issue_dicts[test_type_key],
                issue_from="test",
            )
            processed_issue_key = get_processed_issue_key(record=record)
            self.processed_issues[test_type_key].add(processed_issue_key)

        if should_process_test and not is_test_processed_result:
            handle_test_summary(
                record=record,
                task=task,
                issue_dict=self.issue_dicts.get(test_type_key),
                processed_archs=self.processed_architectures[test_type_key],
            )
            self.processed_tests.add(record["id"])

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
            handle_build_summary(
                record=record,
                builds_summary=self.builds_summary,
                issue_dict=self.issue_dicts["build"],
                tree_index=tree_index,
            )

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

    def _format_processing_for_response(self, hardware_id: str) -> None:
        self.compatibles = list(self.processed_compatibles - {hardware_id})

        self.boots_summary.architectures = list(
            self.processed_architectures["boot"].values()
        )
        self.tests_summary.architectures = list(
            self.processed_architectures["test"].values()
        )

        format_issue_summary_for_response(
            builds_summary=self.builds_summary,
            boots_summary=self.boots_summary,
            tests_summary=self.tests_summary,
            issue_dicts=self.issue_dicts,
        )

    # Using post to receive a body request
    @extend_schema(
        responses=HardwareDetailsSummaryResponse,
        request=HardwareDetailsPostBody,
        methods=["POST"],
    )
    def post(self, request, hardware_id) -> Response:
        try:
            unstable_parse_post_body(instance=self, request=request)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError:
            return Response(
                data={
                    "error": "Invalid body, request body must be a valid json string"
                },
                status=HTTPStatus.BAD_REQUEST,
            )
        except (ValueError, TypeError) as e:
            return Response(
                data={
                    "error": "startTimeStamp and endTimeStamp must be a Unix Timestamp",
                    "exception": str(e),
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

        if len(records) == 0:
            return create_api_error_response(
                error_message="Hardware not found",
                status_code=HTTPStatus.OK,
            )

        is_all_selected = len(self.selected_commits) == 0

        try:
            self._sanitize_records(
                records, trees_with_selected_commits, is_all_selected
            )

            self._format_processing_for_response(hardware_id=hardware_id)

            get_filter_options(
                instance=self,
                records=records,
                selected_trees=trees_with_selected_commits,
                is_all_selected=is_all_selected,
            )

            set_trees_status_summary(
                trees=trees, tree_status_summary=self.tree_status_summary
            )

            valid_response = HardwareDetailsSummaryResponse(
                summary=Summary(
                    builds=self.builds_summary,
                    boots=self.boots_summary,
                    tests=self.tests_summary,
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
                        origins=sorted(self.unfiltered_origins["build"]),
                    ),
                    boots=HardwareTestLocalFilters(
                        issues=list(self.unfiltered_boot_issues),
                        platforms=list(self.unfiltered_boot_platforms),
                        has_unknown_issue=self.unfiltered_uncategorized_issue_flags[
                            "boot"
                        ],
                        origins=sorted(self.unfiltered_origins["boot"]),
                    ),
                    tests=HardwareTestLocalFilters(
                        issues=list(self.unfiltered_test_issues),
                        platforms=list(self.unfiltered_test_platforms),
                        has_unknown_issue=self.unfiltered_uncategorized_issue_flags[
                            "test"
                        ],
                        origins=sorted(self.unfiltered_origins["test"]),
                    ),
                ),
                common=HardwareCommon(
                    trees=trees,
                    compatibles=self.compatibles,
                ),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
