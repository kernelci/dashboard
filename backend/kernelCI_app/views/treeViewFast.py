from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from kernelCI_app.models import Checkouts
from kernelCI_app.typeModels.commonListing import ListingQueryParameters
from kernelCI_app.utils import get_query_time_interval
from http import HTTPStatus
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.typeModels.treeListing import (
    TreeListingFastResponse,
)
from pydantic import ValidationError


class TreeViewFast(APIView):
    @extend_schema(
        responses=TreeListingFastResponse,
        parameters=[ListingQueryParameters],
        methods=["GET"],
    )
    def get(self, request):
        try:
            request_params = ListingQueryParameters(
                origin=(request.GET.get("origin")),
                interval_in_days=request.GET.get("intervalInDays"),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        origin = request_params.origin
        interval_days = request_params.interval_in_days

        interval_days_data = {"days": interval_days}

        checkouts = Checkouts.objects.raw(
            """
            WITH ordered_checkouts AS (
                SELECT
                    id,
                    tree_name,
                    git_repository_branch,
                    git_repository_url,
                    git_commit_hash,
                    git_commit_name,
                    git_commit_tags,
                    patchset_hash,
                    start_time,
                    ROW_NUMBER() OVER
                    (PARTITION BY git_repository_url, git_repository_branch ORDER BY start_time DESC)
                    as time_order
                FROM
                    checkouts
                WHERE
                    origin = %s
                    AND start_time >= TO_TIMESTAMP(%s)
            )
            SELECT
                id,
                tree_name,
                git_repository_branch,
                git_repository_url,
                git_commit_hash,
                git_commit_name,
                git_commit_tags,
                patchset_hash,
                start_time
            FROM
                ordered_checkouts
            WHERE
                time_order = 1
            ORDER BY
                tree_name ASC;
            """,
            [origin, get_query_time_interval(**interval_days_data).timestamp()],
        )

        if not checkouts:
            return create_api_error_response(
                error_message="Trees not found", status_code=HTTPStatus.OK
            )

        response_data = [
            {
                "id": checkout.id,
                "tree_name": checkout.tree_name,
                "git_repository_branch": checkout.git_repository_branch,
                "git_repository_url": checkout.git_repository_url,
                "git_commit_hash": checkout.git_commit_hash,
                "git_commit_name": checkout.git_commit_name,
                "git_commit_tags": checkout.git_commit_tags,
                "patchset_hash": checkout.patchset_hash,
                "start_time": checkout.start_time,
            }
            for checkout in checkouts
        ]

        try:
            valid_response = TreeListingFastResponse(response_data)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
