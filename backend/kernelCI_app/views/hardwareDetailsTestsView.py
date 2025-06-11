from datetime import datetime
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from http import HTTPStatus
import json
from kernelCI_app.helpers.hardwareDetails import (
    assign_default_record_values,
    decide_if_is_full_record_filtered_out,
    decide_if_is_test_in_filter,
    get_trees_with_selected_commit,
    get_validated_current_tree,
    handle_test_history,
    is_test_processed,
    unstable_parse_post_body,
)
from kernelCI_app.queries.hardware import (
    get_hardware_details_data,
    get_hardware_trees_data,
)
from kernelCI_app.typeModels.hardwareDetails import (
    HardwareDetailsPostBody,
    HardwareTestHistoryItem,
    HardwareDetailsTestsResponse,
    Tree,
)
from kernelCI_app.utils import is_boot
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from typing import Dict, List
from kernelCI_app.helpers.errorHandling import create_api_error_response


# disable django csrf protection https://docs.djangoproject.com/en/5.0/ref/csrf/
# that protection is recommended for ‘unsafe’ methods (POST, PUT, and DELETE)
# but we are using POST here just to follow the convention to use the request body
# also the csrf protection require the usage of cookies which is not currently
# supported in this project
@method_decorator(csrf_exempt, name="dispatch")
class HardwareDetailsTests(APIView):
    def __init__(self):
        self.origin: str = None
        self.start_datetime: datetime = None
        self.end_datetime: datetime = None
        self.selected_commits: Dict[str, str] = None

        self.processed_tests = set()

        self.tests: List[HardwareTestHistoryItem] = []

    def _process_test(self, record: Dict) -> None:
        is_record_boot = is_boot(record["path"])
        if is_record_boot:
            return

        is_test_processed_result = is_test_processed(
            record=record, processed_tests=self.processed_tests
        )
        if is_test_processed_result:
            return

        should_process_test = decide_if_is_test_in_filter(
            instance=self,
            test_type="test",
            record=record,
            processed_tests=self.processed_tests,
        )

        if should_process_test:
            handle_test_history(
                record=record,
                task=self.tests,
            )
            self.processed_tests.add(record["id"])

    def _sanitize_records(
        self, records: List[Dict], trees: List[Tree], is_all_selected: bool
    ) -> None:
        for record in records:
            current_tree = get_validated_current_tree(
                record=record, selected_trees=trees
            )
            if current_tree is None:
                continue

            assign_default_record_values(record)

            is_record_filtered_out = decide_if_is_full_record_filtered_out(
                instance=self,
                record=record,
                current_tree=current_tree,
                is_all_selected=is_all_selected,
            )
            if is_record_filtered_out:
                continue

            self._process_test(record=record)

    # Using post to receive a body request
    @extend_schema(
        responses=HardwareDetailsTestsResponse,
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
                error_message="No tests found for this hardware",
                status_code=HTTPStatus.OK,
            )

        is_all_selected = len(self.selected_commits) == 0

        self._sanitize_records(records, trees_with_selected_commits, is_all_selected)

        try:
            valid_response = HardwareDetailsTestsResponse(
                tests=self.tests,
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
