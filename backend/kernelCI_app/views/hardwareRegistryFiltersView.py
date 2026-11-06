from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.queries.hardware import (
    get_hardware_listing_data,
    get_hardware_listing_data_by_revision,
)
from kernelCI_app.queries.hardwareRegistryFilters import (
    get_hardware_registry_filter_options,
)
from kernelCI_app.typeModels.hardwareListing import (
    HardwareQueryParams,
    HardwareRegistryFilterOptions,
    HardwareRegistryFilterOptionsDocumentationOnly,
)
from kernelCI_app.typeModels.hardwareListingByRevision import (
    HardwareListingByRevisionQueryParams,
)


class HardwareRegistryFiltersView(APIView):
    @extend_schema(
        parameters=[HardwareRegistryFilterOptionsDocumentationOnly],
        responses=HardwareRegistryFilterOptions,
    )
    def get(self, request: Request):
        """Options come from the listing rows, so the drawer offers the same boards."""
        try:
            if request.GET.get("git_commit_hash"):
                rows = get_hardware_listing_data_by_revision(
                    **HardwareListingByRevisionQueryParams.from_request(
                        request.GET,
                        tree_name=request.GET.get("tree_name"),
                        git_repository_url=request.GET.get("git_repository_url"),
                        git_repository_branch=request.GET.get("git_repository_branch"),
                        git_commit_hash=request.GET.get("git_commit_hash"),
                    ).model_dump()
                )
            else:
                rows = get_hardware_listing_data(
                    **HardwareQueryParams.from_request(
                        request.GET,
                        start_date=request.GET.get("startTimestampInSeconds"),
                        end_date=request.GET.get("endTimestampInSeconds"),
                        commits_list=request.GET.get("commitsList"),
                    ).model_dump()
                )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        options = get_hardware_registry_filter_options([row[0] for row in rows])
        return Response(
            data=HardwareRegistryFilterOptions(**options).model_dump(),
            status=HTTPStatus.OK,
        )
