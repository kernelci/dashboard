from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from kernelCI_app.helpers.trees import sanitize_tree
from kernelCI_app.queries.tree import get_tree_listing_data
from kernelCI_app.typeModels.commonListing import ListingQueryParameters
from kernelCI_app.helpers.errorHandling import (
    create_api_error_response,
)
from http import HTTPStatus
from kernelCI_app.typeModels.treeListing import (
    Checkout,
    TreeListingResponse,
)
from pydantic import ValidationError

from kernelCI_cache.constants import UNSTABLE_CHECKOUT_THRESHOLD
from kernelCI_cache.queries.tree import get_cached_tree_listing_data


class TreeView(APIView):
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
        interval_param = request_params.interval_in_days

        cached_checkouts = get_cached_tree_listing_data(
            origin=origin_param,
            interval_in_days=interval_param,
            min_age_in_days=min(interval_param, UNSTABLE_CHECKOUT_THRESHOLD),
        )

        has_cache = cached_checkouts is not None and len(cached_checkouts) > 0
        kcidb_interval = (
            min(interval_param, UNSTABLE_CHECKOUT_THRESHOLD)
            if has_cache
            else interval_param
        )

        kcidb_checkouts = get_tree_listing_data(
            origin=origin_param,
            interval_in_days=kcidb_interval,
        )

        if not cached_checkouts and not kcidb_checkouts:
            return create_api_error_response(
                error_message="Trees not found", status_code=HTTPStatus.OK
            )

        # This set is only meant to remove the duplicate cases when the
        # checkout is present in both the cache and in kcidb in the last x days.
        # It saves the kcidb tree_name as part of the key, such that it doesn't skip
        # trees with the same branch and git_url but different tree_name.
        unique_trees: set[tuple[str, str, str]] = set()
        checkouts: list[Checkout] = []

        for checkout in kcidb_checkouts + list(cached_checkouts):
            tree_name = checkout["tree_name"]
            git_branch = checkout["git_repository_branch"]
            git_url = checkout["git_repository_url"]

            kcidb_identifier = (
                tree_name,
                git_branch,
                git_url,
            )
            if kcidb_identifier not in unique_trees:
                unique_trees.add(kcidb_identifier)
                typed_checkout = sanitize_tree(checkout=checkout)
                checkouts.append(typed_checkout)

        try:
            valid_response = TreeListingResponse(checkouts)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump(by_alias=True))
