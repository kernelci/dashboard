from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.queries.hardwareRegistryFilters import (
    get_hardware_registry_filter_options,
)
from kernelCI_app.typeModels.hardwareListing import (
    HardwareQueryParams,
    HardwareRegistryFilterOptions,
    HardwareRegistryFilterOptionsDocumentationOnly,
)


class HardwareRegistryFiltersView(APIView):
    @extend_schema(
        parameters=[HardwareRegistryFilterOptionsDocumentationOnly],
        responses=HardwareRegistryFilterOptions,
    )
    def get(self, request: Request):
        try:
            query_params = HardwareQueryParams(
                start_date=request.GET.get("startTimestampInSeconds"),
                end_date=request.GET.get("endTimestampInSeconds"),
                origin=request.GET.get("origin"),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        options = get_hardware_registry_filter_options(
            origin=query_params.origin,
            start_date=query_params.start_date,
            end_date=query_params.end_date,
            tree_name=request.GET.get("tree_name"),
            git_repository_url=request.GET.get("git_repository_url"),
            git_repository_branch=request.GET.get("git_repository_branch"),
            git_commit_hash=request.GET.get("git_commit_hash"),
        )
        return Response(
            data=HardwareRegistryFilterOptions(**options).model_dump(),
            status=HTTPStatus.OK,
        )
