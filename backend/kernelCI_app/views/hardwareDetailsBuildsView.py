import json
from datetime import datetime
from http import HTTPStatus
from typing import Dict, List, Set

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.helpers.hardwareDetails import (
    assign_default_record_values,
    decide_if_is_build_in_filter,
    decide_if_is_full_record_filtered_out,
    get_build_typed,
    get_trees_with_selected_commit,
    get_validated_current_tree,
    handle_build_history,
    unstable_parse_post_body,
)
from kernelCI_app.queries.hardware import (
    get_hardware_details_data,
    get_hardware_trees_data,
)
from kernelCI_app.typeModels.commonOpenApiParameters import (
    HARDWARE_ID_PATH_PARAM,
)
from kernelCI_app.typeModels.hardwareDetails import (
    HardwareBuildHistoryItem,
    HardwareDetailsBuildsResponse,
    HardwareDetailsPostBody,
    Tree,
)
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.constants.localization import ClientStrings


# disable django csrf protection https://docs.djangoproject.com/en/5.0/ref/csrf/
# that protection is recommended for ‘unsafe’ methods (POST, PUT, and DELETE)
# but we are using POST here just to follow the convention to use the request body
# also the csrf protection require the usage of cookies which is not currently
# supported in this project
@method_decorator(csrf_exempt, name="dispatch")
class HardwareDetailsBuilds(APIView):
    def __init__(self):
        self.origin: str = None
        self.start_datetime: datetime = None
        self.end_datetime: datetime = None
        self.selected_commits: Dict[str, str] = None

        self.filters: FilterParams = None

        self.processed_builds: Set[str] = set()
        self.builds: List[HardwareBuildHistoryItem] = []

    def _process_build(self, *, record: dict, tree_index: int) -> None:
        build = get_build_typed(record, tree_index)

        should_process_build = decide_if_is_build_in_filter(
            instance=self,
            build=build,
            processed_builds=self.processed_builds,
            incident_test_id=record["incidents__test_id"],
        )

        self.processed_builds.add(build.id)
        if should_process_build:
            handle_build_history(
                record=record,
                tree_idx=tree_index,
                builds=self.builds,
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

            tree_index = current_tree.index

            is_record_filtered_out = decide_if_is_full_record_filtered_out(
                instance=self,
                record=record,
                current_tree=current_tree,
                is_all_selected=is_all_selected,
            )

            if is_record_filtered_out:
                continue

            self._process_build(record=record, tree_index=tree_index)

    @extend_schema(
        parameters=[HARDWARE_ID_PATH_PARAM],
        request=HardwareDetailsPostBody,
        methods=["POST"],
        responses=HardwareDetailsBuildsResponse,
    )
    def post(self, request, hardware_id) -> Response:
        try:
            unstable_parse_post_body(instance=self, request=request)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)
        except json.JSONDecodeError:
            return Response(
                data={"error": ClientStrings.INVALID_JSON_BODY},
                status=HTTPStatus.BAD_REQUEST,
            )
        except (ValueError, TypeError):
            return Response(
                data={"error": ClientStrings.INVALID_TIMESTAMP},
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
                error_message=ClientStrings.HARDWARE_NO_COMMITS,
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
                error_message=ClientStrings.HARDWARE_BUILDS_NOT_FOUND,
                status_code=HTTPStatus.OK,
            )

        is_all_selected = len(self.selected_commits) == 0

        try:
            self._sanitize_records(
                records, trees_with_selected_commits, is_all_selected
            )

            valid_response = HardwareDetailsBuildsResponse(
                builds=self.builds,
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
