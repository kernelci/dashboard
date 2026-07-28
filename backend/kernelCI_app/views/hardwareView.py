from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.constants.localization import ClientStrings, DocStrings
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.queries.hardware import (
    get_hardware_filters,
    get_hardware_listing_data,
)
from kernelCI_app.typeModels.commonListing import ListingStatusCount
from kernelCI_app.typeModels.hardwareListing import (
    HardwareFiltersQueryParams,
    HardwareFiltersQueryParamsDocumentationOnly,
    HardwareFiltersResponse,
    HardwareListingItem,
    HardwareListingResponse,
    HardwareQueryParams,
    HardwareQueryParamsDocumentationOnly,
)


class HardwareView(APIView):
    def _sanitize_records(
        self, hardwares_raw: list[tuple]
    ) -> list[HardwareListingItem]:
        hardwares = []
        for hardware in hardwares_raw:
            hardwares.append(
                HardwareListingItem(
                    platform=hardware[0],
                    hardware=hardware[1],
                    build_status_summary=ListingStatusCount(
                        PASS=hardware[2],
                        FAIL=hardware[3],
                        INCONCLUSIVE=hardware[4],
                    ),
                    boot_status_summary=ListingStatusCount(
                        PASS=hardware[5],
                        FAIL=hardware[6],
                        INCONCLUSIVE=hardware[7],
                    ),
                    test_status_summary=ListingStatusCount(
                        PASS=hardware[8],
                        FAIL=hardware[9],
                        INCONCLUSIVE=hardware[10],
                    ),
                )
            )

        return hardwares

    @extend_schema(
        parameters=[HardwareQueryParamsDocumentationOnly],
        responses=HardwareListingResponse,
    )
    def get(self, request: Request):
        try:
            query_params = HardwareQueryParams(
                start_date=request.GET.get("startTimestampInSeconds"),
                end_date=request.GET.get("endTimestampInSeconds"),
                # "origin" is the deprecated alias of "testOrigin"
                test_origin=request.GET.get("testOrigin")
                or request.GET.get("origin")
                or None,
                commits_list=request.GET.get("commitsList"),
                checkout_origin=request.GET.get("checkoutOrigin"),
                build_origin=request.GET.get("buildOrigin"),
                build_lab=request.GET.get("buildLab"),
                test_lab=request.GET.get("testLab"),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        hardwares_raw = get_hardware_listing_data(
            start_date=query_params.start_date,
            end_date=query_params.end_date,
            checkout_origin=query_params.checkout_origin,
            build_origin=query_params.build_origin,
            build_lab=query_params.build_lab,
            test_origin=query_params.test_origin,
            test_lab=query_params.test_lab,
            commits_list=query_params.commits_list,
        )

        try:
            sanitized_records = self._sanitize_records(hardwares_raw=hardwares_raw)
            result = HardwareListingResponse(hardware=sanitized_records)

            if len(result.hardware) < 1:
                return create_api_error_response(
                    error_message=ClientStrings.NO_HARDWARE_FOUND,
                    status_code=HTTPStatus.OK,
                )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(data=result.model_dump(), status=HTTPStatus.OK)


class HardwareFiltersView(APIView):
    """Values available for each hardware listing filter."""

    @extend_schema(
        parameters=[HardwareFiltersQueryParamsDocumentationOnly],
        responses=HardwareFiltersResponse,
        description=DocStrings.HARDWARE_FILTERS_DESCRIPTION,
    )
    def get(self, request: Request):
        try:
            query_params = HardwareFiltersQueryParams(
                start_date=request.GET.get("startTimestampInSeconds"),
                end_date=request.GET.get("endTimestampInSeconds"),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        filters = get_hardware_filters(
            start_date=query_params.start_date,
            end_date=query_params.end_date,
        )

        try:
            result = HardwareFiltersResponse(**filters)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(data=result.model_dump(), status=HTTPStatus.OK)
