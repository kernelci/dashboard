from collections import defaultdict
from datetime import datetime
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from http import HTTPStatus
from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.helpers.hardwareDetails import (
    assign_default_record_values,
    decide_if_is_build_in_filter,
    decide_if_is_full_record_filtered_out,
    decide_if_is_test_in_filter,
    generate_test_dict,
    generate_tree_status_summary_dict,
    get_build,
    get_filter_options,
    get_hardware_details_data,
    get_hardware_trees_data,
    get_trees_with_selected_commit,
    get_trees_with_status_summary,
    get_validated_current_tree,
    handle_build,
    handle_test_or_boot,
    handle_tree_status_summary,
    mutate_properties_to_list,
    unstable_parse_post_body,
)
from kernelCI_app.typeModels.hardwareDetails import (
    HardwareDetailsFullResponse,
    HardwareTreeList,
    PossibleTestType,
)
from kernelCI_app.utils import (
    is_boot
)
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

        self.builds = {
            "items": [],
            "issues": {},
            "failedWithUnknownIssues": 0,
        }
        self.boots = generate_test_dict()
        self.tests = generate_test_dict()

        self.tree_status_summary = defaultdict(generate_tree_status_summary_dict)
        self.compatibles: List[str] = []

    def _process_test(self, record: Dict) -> None:
        is_record_boot = is_boot(record["path"])
        test_filter_key: PossibleTestType = "boot" if is_record_boot else "test"

        is_record_processed = record["id"] in self.processed_tests
        is_test_in_filter = decide_if_is_test_in_filter(
            instance=self, test_type=test_filter_key, record=record
        )

        should_process_test = not is_record_processed and is_test_in_filter

        if should_process_test:
            self.processed_tests.add(record["id"])
            handle_test_or_boot(record, self.boots if is_record_boot else self.tests)

    def _process_build(self, record: Dict, tree_index: int) -> None:
        build = get_build(record, tree_index)
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
        self, records, trees: HardwareTreeList, is_all_selected: bool
    ) -> None:
        compatibles: Set[str] = set()

        for record in records:
            current_tree = get_validated_current_tree(
                record=record, selected_trees=trees
            )
            if current_tree is None:
                continue

            assign_default_record_values(record)

            if record["environment_compatible"] is not None:
                compatibles.update(record["environment_compatible"])

            tree_index = current_tree["index"]

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

        self.builds["summary"] = create_details_build_summary(self.builds["items"])
        self.compatibles = list(compatibles)
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
    )
    def post(self, request, hardware_id):
        try:
            unstable_parse_post_body(instance=self, request=request)
        except ValidationError as e:
            return Response(data={"error": e.json()}, status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError:
            return Response(
                data={"error": "Invalid body, request body must be a valid json string"},
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
            return Response(
                data={"error": "Hardware not found"}, status=HTTPStatus.NOT_FOUND
            )

        is_all_selected = len(self.selected_commits) == 0

        self._sanitize_records(records, trees_with_selected_commits, is_all_selected)

        configs, archs, compilers = get_filter_options(
            records=records,
            selected_trees=trees_with_selected_commits,
            is_all_selected=is_all_selected,
        )

        trees_with_status_summary = get_trees_with_status_summary(
            trees=trees, tree_status_summary=self.tree_status_summary
        )

        response = {
            "builds": self.builds["items"],
            "boots": self.boots["history"],
            "tests": self.tests["history"],
            "summary": {
                "builds": {
                    "status": self.builds["summary"]["builds"],
                    "architectures": self.builds["summary"]["architectures"],
                    "configs": self.builds["summary"]["configs"],
                    "issues": self.builds["issues"],
                    "unknown_issues": self.builds["failedWithUnknownIssues"],
                },
                "boots": {
                    "status": self.boots["statusSummary"],
                    "architectures": self.boots["archSummary"],
                    "configs": self.boots["configs"],
                    "issues": self.boots["issues"],
                    "unknown_issues": self.boots["failedWithUnknownIssues"],
                    "platforms": self.boots["platforms"],
                    "fail_reasons": self.boots["failReasons"],
                    "failed_platforms": list(self.boots["platformsFailing"]),
                },
                "tests": {
                    "status": self.tests["statusSummary"],
                    "architectures": self.tests["archSummary"],
                    "configs": self.tests["configs"],
                    "issues": self.tests["issues"],
                    "unknown_issues": self.tests["failedWithUnknownIssues"],
                    "platforms": self.tests["platforms"],
                    "fail_reasons": self.tests["failReasons"],
                    "failed_platforms": list(self.tests["platformsFailing"]),

                },
                "trees": trees_with_status_summary,
                "configs": configs,
                "architectures": archs,
                "compilers": compilers,
                "compatibles": self.compatibles,
            }
        }
        try:
            valid_response = HardwareDetailsFullResponse(**response)
        except ValidationError as e:
            return Response(data=e.errors(), status=HTTPStatus.BAD_REQUEST)

        return Response(data=valid_response.model_dump(), status=HTTPStatus.OK)
