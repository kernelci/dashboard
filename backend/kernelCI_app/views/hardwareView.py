from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.queries.hardware import get_hardware_listing_data
from kernelCI_app.typeModels.hardwareListing import (
    HardwareListingItem,
    HardwareListingResponse,
    HardwareQueryParams,
    HardwareQueryParamsDocumentationOnly,
)


class HardwareView(APIView):
    @extend_schema(
        parameters=[HardwareQueryParamsDocumentationOnly],
        responses=HardwareListingResponse,
    )
    def get(self, request: Request):
        try:
            query_params = HardwareQueryParams.from_request(
                request.GET,
                start_date=request.GET.get("startTimestampInSeconds"),
                end_date=request.GET.get("endTimestampInSeconds"),
                commits_list=request.GET.get("commitsList"),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        hardwares_raw = get_hardware_listing_data(
            start_date=query_params.start_date,
            end_date=query_params.end_date,
            checkout_origin=query_params.checkout_origin,
            build_origin=query_params.build_origin,
            test_origin=query_params.test_origin,
            build_lab=query_params.build_lab,
            test_lab=query_params.test_lab,
            commits_list=query_params.commits_list,
        )

        try:
            result = HardwareListingResponse(
                hardware=[HardwareListingItem.from_row(row) for row in hardwares_raw]
            )

            if len(result.hardware) < 1:
                return create_api_error_response(
                    error_message=ClientStrings.NO_HARDWARE_FOUND,
                    status_code=HTTPStatus.OK,
                )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(data=result.model_dump(), status=HTTPStatus.OK)
