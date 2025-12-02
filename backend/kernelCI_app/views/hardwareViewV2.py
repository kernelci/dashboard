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
from kernelCI_app.typeModels.hardwareListingV2 import (
    HardwareItemV2,
    HardwareQueryParamsV2,
    HardwareQueryParamsV2DocumentationOnly,
    HardwareListingResponseV2,
    StatusCountV2,
)
from kernelCI_app.queries.hardware import (
    get_hardware_listing_data_from_status_table,
)
from kernelCI_app.constants.localization import ClientStrings


class HardwareViewV2(APIView):
    def _sanitize_records(self, hardwares_raw: list[tuple]) -> list[HardwareItemV2]:
        hardwares = []
        for hardware in hardwares_raw:
            hardwares.append(
                HardwareItemV2(
                    platform=hardware[0],
                    hardware=hardware[1],
                    build_status_summary=StatusCountV2(
                        PASS=hardware[2],
                        FAIL=hardware[3],
                        INCONCLUSIVE=hardware[4],
                    ),
                    boot_status_summary=StatusCountV2(
                        PASS=hardware[5],
                        FAIL=hardware[6],
                        INCONCLUSIVE=hardware[7],
                    ),
                    test_status_summary=StatusCountV2(
                        PASS=hardware[8],
                        FAIL=hardware[9],
                        INCONCLUSIVE=hardware[10],
                    ),
                )
            )

        return hardwares

    @extend_schema(
        parameters=[HardwareQueryParamsV2DocumentationOnly],
        responses=HardwareListingResponseV2,
    )
    def get(self, request: Request):
        try:
            query_params = HardwareQueryParamsV2(
                start_date=request.GET.get("startTimestampInSeconds"),
                end_date=request.GET.get("endTimestampInSeconds"),
                origin=request.GET.get("origin"),
            )

            start_date: datetime = query_params.start_date
            end_date: datetime = query_params.end_date
            origin = query_params.origin
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        hardwares_raw = get_hardware_listing_data_from_status_table(
            origin=origin,
            start_date=start_date,
            end_date=end_date,
        )

        try:
            sanitized_records = self._sanitize_records(hardwares_raw=hardwares_raw)
            result = HardwareListingResponseV2(hardware=sanitized_records)

            if len(result.hardware) < 1:
                return create_api_error_response(
                    error_message=ClientStrings.NO_HARDWARE_FOUND,
                    status_code=HTTPStatus.OK,
                )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(data=result.model_dump(), status=HTTPStatus.OK)
