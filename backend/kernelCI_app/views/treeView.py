from typing import Dict
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from kernelCI_app.typeModels.commonListing import ListingQueryParameters
from kernelCI_app.helpers.errorHandling import (
    create_api_error_response,
)
from kernelCI_cache.checkouts import populate_checkouts_cache_db
from kernelCI_app.queries.tree import get_tree_listing_data
from http import HTTPStatus
from kernelCI_app.typeModels.treeListing import (
    TreeListingResponse,
)
from pydantic import ValidationError


class TreeView(APIView):
    def _sanitize_tree(self, checkout: Dict) -> Dict:
        build_status = {
            "PASS": checkout[8],
            "FAIL": checkout[9],
            "NULL": checkout[10],
            "ERROR": checkout[11],
            "MISS": checkout[12],
            "DONE": checkout[13],
            "SKIP": checkout[14],
        }

        test_status = {
            "fail": checkout[15],
            "error": checkout[16],
            "miss": checkout[17],
            "pass": checkout[18],
            "done": checkout[19],
            "skip": checkout[20],
            "null": checkout[21],
        }

        boot_status = {
            "fail": checkout[22],
            "error": checkout[23],
            "miss": checkout[24],
            "pass": checkout[25],
            "done": checkout[26],
            "skip": checkout[27],
            "null": checkout[28],
        }

        return {
            "git_repository_branch": checkout[2],
            "git_repository_url": checkout[3],
            "git_commit_hash": checkout[4],
            "git_commit_tags": checkout[5],
            "git_commit_name": checkout[6],
            "start_time": checkout[7],
            "build_status": {**build_status},
            "test_status": {**test_status},
            "boot_status": {**boot_status},
            "tree_names": checkout[29],
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
            populate_checkouts_cache_db(checkouts, origin_param)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump(by_alias=True))
