from http import HTTPStatus
from typing import Dict, List
from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from kernelCI_app.helpers.errorHandling import create_error_response
from kernelCI_app.helpers.filters import (
    FilterParams,
)
from kernelCI_app.helpers.treeDetails import (
    decide_if_is_build_filtered_out,
    decide_if_is_full_row_filtered_out,
    get_build,
    get_current_row_data,
    get_tree_details_data,
)
from kernelCI_app.typeModels.treeDetails import (
    TreeDetailsBuildsResponse,
    TreeQueryParameters,
)
from kernelCI_app.constants.general import MAESTRO_DUMMY_BUILD_PREFIX


class TreeDetailsBuilds(APIView):
    def __init__(self):
        self.filters = None

        self.builds: List[Dict] = []
        self.processed_builds = set()
        self.tree_url = ""

    def _process_builds(self, row_data):
        build_id = row_data["build_id"]

        if decide_if_is_build_filtered_out(self, row_data):
            return

        if build_id in self.processed_builds:
            return

        self.processed_builds.add(build_id)

        build_item = get_build(row_data)

        self.builds.append(build_item)

    def _sanitize_rows(self, rows):
        for row in rows:
            row_data = get_current_row_data(row)

            is_record_filter_out = decide_if_is_full_row_filtered_out(self, row_data)

            if is_record_filter_out:
                continue

            if row_data["build_id"] is not None and not row_data["build_id"].startswith(
                MAESTRO_DUMMY_BUILD_PREFIX
            ):
                self._process_builds(row_data)

    @extend_schema(
        parameters=[TreeQueryParameters],
        responses=TreeDetailsBuildsResponse,
        methods=["GET"],
    )
    def get(self, request, commit_hash: str | None):
        rows = get_tree_details_data(request, commit_hash)

        self.filters = FilterParams(request)

        if len(rows) == 0:
            return create_error_response(
                error_message="No builds found for this tree", status_code=HTTPStatus.OK
            )

        self._sanitize_rows(rows)

        try:
            valid_response = TreeDetailsBuildsResponse(
                builds=self.builds,
            )
        except ValidationError as e:
            return Response(data=e.errors(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(data=valid_response.model_dump(), status=HTTPStatus.OK)
