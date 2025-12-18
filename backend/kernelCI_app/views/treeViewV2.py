from http import HTTPStatus
from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from kernelCI_app.queries.tree import get_tree_listing_data_denormalized
from kernelCI_app.typeModels.commonListing import ListingQueryParameters, StatusCountV2
from kernelCI_app.typeModels.treeListing import TreeListingItem, TreeListingResponseV2
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.constants.localization import ClientStrings


class TreeViewV2(APIView):
    def _sanitize_records(self, trees_raw: list[tuple]) -> list[TreeListingItem]:
        trees = []
        for tree in trees_raw:
            trees.append(
                TreeListingItem(
                    checkout_id=tree[0],
                    origin=tree[1],
                    tree_name=tree[2],
                    git_repository_url=tree[3],
                    git_repository_branch=tree[4],
                    git_commit_hash=tree[5],
                    git_commit_name=tree[6],
                    git_commit_tags=tree[7],
                    start_time=tree[8],
                    build_status=StatusCountV2(
                        PASS=tree[9],
                        FAIL=tree[10],
                        INCONCLUSIVE=tree[11],
                    ),
                    boot_status=StatusCountV2(
                        PASS=tree[12],
                        FAIL=tree[13],
                        INCONCLUSIVE=tree[14],
                    ),
                    test_status=StatusCountV2(
                        PASS=tree[15],
                        FAIL=tree[16],
                        INCONCLUSIVE=tree[17],
                    ),
                )
            )

        return trees

    @extend_schema(
        parameters=[ListingQueryParameters],
        responses=TreeListingResponseV2,
    )
    def get(self, request: HttpRequest):
        try:
            query_params = ListingQueryParameters(
                origin=request.GET.get("origin"),
                interval_in_days=request.GET.get("interval_in_days"),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        trees_raw = get_tree_listing_data_denormalized(
            origin=query_params.origin,
            interval_in_days=query_params.interval_in_days,
        )

        if not trees_raw:
            return create_api_error_response(
                error_message=ClientStrings.NO_TREES_FOUND,
                status_code=HTTPStatus.OK,
            )

        try:
            sanitized_records = self._sanitize_records(trees_raw=trees_raw)
            result = TreeListingResponseV2(sanitized_records)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(data=result.model_dump(), status=HTTPStatus.OK)
