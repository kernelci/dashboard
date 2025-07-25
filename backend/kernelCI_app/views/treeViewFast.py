from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from kernelCI_app.queries.tree import get_tree_listing_fast
from kernelCI_app.typeModels.commonListing import ListingQueryParameters
from http import HTTPStatus
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.typeModels.treeListing import (
    CheckoutFast,
    TreeListingFastResponse,
)
from pydantic import ValidationError
from kernelCI_app.constants.localization import ClientStrings


class TreeViewFast(APIView):
    @extend_schema(
        responses=TreeListingFastResponse,
        parameters=[ListingQueryParameters],
        methods=["GET"],
    )
    def get(self, request: HttpRequest) -> Response:
        try:
            request_params = ListingQueryParameters(
                origin=(request.GET.get("origin")),
                interval_in_days=request.GET.get("interval_in_days"),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        origin = request_params.origin
        interval_days = request_params.interval_in_days

        interval_days_data = {"days": interval_days}

        checkouts = get_tree_listing_fast(
            origin=origin,
            interval=interval_days_data,
        )

        if not checkouts:
            return create_api_error_response(
                error_message=ClientStrings.NO_TREES_FOUND, status_code=HTTPStatus.OK
            )

        response_data: list[CheckoutFast] = []

        for checkout in checkouts:
            response_data.append(
                CheckoutFast(
                    id=checkout.id,
                    tree_name=checkout.tree_name,
                    origin=checkout.origin,
                    git_repository_branch=checkout.git_repository_branch,
                    git_repository_url=checkout.git_repository_url,
                    git_commit_hash=checkout.git_commit_hash,
                    git_commit_name=checkout.git_commit_name,
                    git_commit_tags=checkout.git_commit_tags,
                    patchset_hash=checkout.patchset_hash,
                    start_time=checkout.start_time,
                    origin_builds_finish_time=checkout.origin_builds_finish_time,
                    origin_tests_finish_time=checkout.origin_tests_finish_time,
                )
            )

        try:
            valid_response = TreeListingFastResponse(response_data)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
