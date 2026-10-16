from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.queries.hardware import get_hardware_listing_data_by_revision
from kernelCI_app.typeModels.hardwareListing import (
    HardwareListingItem,
    HardwareListingResponse,
)
from kernelCI_app.typeModels.hardwareListingByRevision import (
    HardwareListingByRevisionQueryParams,
    HardwareListingByRevisionQueryParamsDocumentationOnly,
)


class HardwareByRevisionView(APIView):
    @extend_schema(
        parameters=[HardwareListingByRevisionQueryParamsDocumentationOnly],
        responses=HardwareListingResponse,
    )
    def get(self, request: Request):
        try:
            query_params = HardwareListingByRevisionQueryParams.from_request(
                request.GET,
                tree_name=request.GET.get("tree_name"),
                git_repository_url=request.GET.get("git_repository_url"),
                git_repository_branch=request.GET.get("git_repository_branch"),
                git_commit_hash=request.GET.get("git_commit_hash"),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        hardwares_raw = get_hardware_listing_data_by_revision(
            checkout_origin=query_params.checkout_origin,
            build_origin=query_params.build_origin,
            test_origin=query_params.test_origin,
            build_lab=query_params.build_lab,
            test_lab=query_params.test_lab,
            tree_name=query_params.tree_name,
            git_repository_url=query_params.git_repository_url,
            git_repository_branch=query_params.git_repository_branch,
            git_commit_hash=query_params.git_commit_hash,
        )

        try:
            result = HardwareListingResponse(
                hardware=[HardwareListingItem.from_row(row) for row in hardwares_raw]
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(data=result.model_dump(), status=HTTPStatus.OK)
