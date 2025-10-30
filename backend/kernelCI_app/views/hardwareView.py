from datetime import datetime
from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from kernelCI_app.helpers.errorHandling import (
    create_api_error_response,
)
from kernelCI_app.typeModels.hardwareListing import (
    HardwareItem,
    HardwareQueryParams,
    HardwareQueryParamsDocumentationOnly,
    HardwareListingResponse,
)
from kernelCI_app.queries.hardware import get_hardware_listing_data
from kernelCI_app.constants.localization import ClientStrings


class HardwareView(APIView):
    def _sanitize_records(self, hardwares_raw: list[tuple]) -> list[HardwareItem]:
        hardwares = []
        for hardware in hardwares_raw:
            hardwares.append(
                HardwareItem(
                    platform=hardware[0],
                    hardware=hardware[1],
                    build_status_summary={
                        "PASS": hardware[2],
                        "FAIL": hardware[3],
                        "NULL": hardware[4],
                        "ERROR": hardware[5],
                        "MISS": hardware[6],
                        "DONE": hardware[7],
                        "SKIP": hardware[8],
                    },
                    boot_status_summary={
                        "PASS": hardware[9],
                        "FAIL": hardware[10],
                        "NULL": hardware[11],
                        "ERROR": hardware[12],
                        "MISS": hardware[13],
                        "DONE": hardware[14],
                        "SKIP": hardware[15],
                    },
                    test_status_summary={
                        "PASS": hardware[16],
                        "FAIL": hardware[17],
                        "NULL": hardware[18],
                        "ERROR": hardware[19],
                        "MISS": hardware[20],
                        "DONE": hardware[21],
                        "SKIP": hardware[22],
                    },
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
                origin=request.GET.get("origin"),
            )

            start_date: datetime = query_params.start_date
            end_date: datetime = query_params.end_date
            origin = query_params.origin
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        hardwares_raw = get_hardware_listing_data(
            origin=origin,
            start_date=start_date,
            end_date=end_date,
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
