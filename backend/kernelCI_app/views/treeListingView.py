from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.helpers.errorHandling import create_api_error_response
from rest_framework.views import APIView
from rest_framework.response import Response
from kernelCI_app.helpers.trees import sanitize_tree
from kernelCI_app.typeModels.commonListing import ListingQueryParameters
from http import HTTPStatus
from kernelCI_app.typeModels.treeListing import TreeListingResponse
from pydantic import ValidationError

from django.db import connections


# TODO: move to queries folder
# TODO: add unit tests
# TODO: stop using relative intervals!
def get_new_tree_listing_data(origin: str, interval_in_days: int) -> list[dict]:
    """
    Fetches data from the tree_listing table for direct use in the frontend.
    The status counts are NOT grouped in the return.
    """

    query = """
        SELECT
            id,
            _timestamp,
            checkout_id,
            origin,
            tree_name,
            git_repository_url,
            git_repository_branch,
            git_commit_hash,
            git_commit_name,
            git_commit_tags,
            start_time,
            origin_builds_finish_time,
            origin_tests_finish_time,

            pass_builds,
            fail_builds,
            done_builds,
            miss_builds,
            skip_builds,
            error_builds,
            null_builds,

            pass_boots,
            fail_boots,
            done_boots,
            miss_boots,
            skip_boots,
            error_boots,
            null_boots,

            pass_tests,
            fail_tests,
            done_tests,
            miss_tests,
            skip_tests,
            error_tests,
            null_tests
        FROM
            tree_listing
        WHERE
            origin = %s
            AND start_time >= NOW() - INTERVAL '%s days'
    """

    params = [origin, interval_in_days]

    with connections["default"].cursor() as cursor:
        cursor.execute(query, params)
        result = dict_fetchall(cursor)

    return result


class TreeListingView(APIView):
    @extend_schema(
        responses=TreeListingResponse,
        parameters=[ListingQueryParameters],
        methods=["GET"],
    )
    def get(self, request: HttpRequest) -> Response:
        """
        Returns the checkout data for trees in a specific origin, in the last X days.
        The data includes the number of builds, boots and tests, grouped by status, for each checkout.

        Query params (`ListingQueryParameters`):
            - origin: str
            - interval_in_days: int

        Status returns:
            - 200: A list of checkouts with their respective data.
            - 400: Bad request, invalid parameters.
            - 500: Internal server error, something went wrong on the server. Usually validation.
        """

        try:
            request_params = ListingQueryParameters(
                origin=request.GET.get("origin"),
                interval_in_days=request.GET.get("interval_in_days"),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        rows = get_new_tree_listing_data(
            origin=request_params.origin,
            interval_in_days=request_params.interval_in_days,
        )

        if not rows:
            return create_api_error_response(
                error_message=ClientStrings.NO_TREES_FOUND, status_code=HTTPStatus.OK
            )

        try:
            valid_response = TreeListingResponse(
                root=[sanitize_tree(row) for row in rows]
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump(by_alias=True))
