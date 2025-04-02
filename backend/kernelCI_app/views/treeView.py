from typing import Dict
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from kernelCI_app.typeModels.commonListing import ListingQueryParameters
from kernelCI_app.helpers.errorHandling import (
    create_api_error_response,
)
from kernelCI_app.queries.tree import get_tree_listing_data
from http import HTTPStatus
from kernelCI_app.typeModels.treeListing import (
    TreeListingResponse,
)
from pydantic import ValidationError


class TreeView(APIView):
    def _sanitize_tree(self, checkout: Dict) -> Dict:
        build_status = {
            "PASS": checkout[10],
            "FAIL": checkout[11],
            "NULL": checkout[12],
            "ERROR": checkout[13],
            "MISS": checkout[14],
            "DONE": checkout[15],
            "SKIP": checkout[16],
        }

        test_status = {
            "fail": checkout[17],
            "error": checkout[18],
            "miss": checkout[19],
            "pass": checkout[20],
            "done": checkout[21],
            "skip": checkout[22],
            "null": checkout[23],
        }

        boot_status = {
            "fail": checkout[24],
            "error": checkout[25],
            "miss": checkout[26],
            "pass": checkout[27],
            "done": checkout[28],
            "skip": checkout[29],
            "null": checkout[30],
        }

        return {
            "id": checkout[0],
            "git_repository_branch": checkout[2],
            "git_repository_url": checkout[3],
            "git_commit_hash": checkout[4],
            "origin_builds_finish_time": checkout[5],
            "origin_tests_finish_time": checkout[6],
            "git_commit_tags": checkout[7],
            "git_commit_name": checkout[8],
            "start_time": checkout[9],
            "build_status": {**build_status},
            "test_status": {**test_status},
            "boot_status": {**boot_status},
            "tree_names": checkout[31],
        }

    @extend_schema(
        responses=TreeListingResponse,
        parameters=[ListingQueryParameters],
        methods=["GET"],
    )
    def get(self, request) -> Response:
        try:
            request_params = ListingQueryParameters(
                origin=request.GET.get("origin"),
                interval_in_days=request.GET.get("intervalInDays"),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        origin_param = request_params.origin
        interval_days = request_params.interval_in_days

        interval_days_data = {"days": interval_days}

        checkouts = get_tree_listing_data(
            origin=origin_param,
            interval_in_days=interval_days_data,
        )

        if not checkouts:
            return create_api_error_response(
                error_message="Trees not found", status_code=HTTPStatus.OK
            )

        checkouts = [self._sanitize_tree(checkout) for checkout in checkouts]

        try:
            valid_response = TreeListingResponse(checkouts)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump(by_alias=True))
