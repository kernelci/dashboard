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
from kernelCI_app.constants.general import UNKNOWN_STRING
from kernelCI_app.typeModels.hardwareListing import (
    HardwareItem,
    HardwareQueryParams,
    HardwareQueryParamsDocumentationOnly,
    HardwareResponse,
)
from kernelCI_app.queries.hardware import get_hardware_listing_data


class HardwareView(APIView):
    def _get_tests_from_database(
        self, start_date: datetime, end_date: datetime, origin: str
    ) -> list[HardwareItem]:
        hardwares_raw = get_hardware_listing_data(
            origin=origin,
            start_date=start_date,
            end_date=end_date,
        )

        # TODO Move this logic to the pydantic model
        hardwares = []
        for hardware in hardwares_raw:
            platform = ""
            match len(hardware["platform"]):
                case 0:
                    platform = UNKNOWN_STRING
                case 1:
                    platform = hardware["platform"][0]
                case _:
                    platform = hardware["platform"]

            hardwares.append(
                HardwareItem(
                    hardware_name=hardware["hardware"],
                    platform=platform,
                    test_status_summary={
                        "FAIL": hardware["fail_tests"],
                        "ERROR": hardware["error_tests"],
                        "MISS": hardware["miss_tests"],
                        "PASS": hardware["pass_tests"],
                        "DONE": hardware["done_tests"],
                        "SKIP": hardware["skip_tests"],
                        "NULL": hardware["null_tests"],
                    },
                    boot_status_summary={
                        "FAIL": hardware["fail_boots"],
                        "ERROR": hardware["error_boots"],
                        "MISS": hardware["miss_boots"],
                        "PASS": hardware["pass_boots"],
                        "DONE": hardware["done_boots"],
                        "SKIP": hardware["skip_boots"],
                        "NULL": hardware["null_boots"],
                    },
                    build_status_summary={
                        "PASS": hardware["pass_builds"],
                        "FAIL": hardware["fail_builds"],
                        "NULL": hardware["null_builds"],
                        "ERROR": hardware["error_builds"],
                        "MISS": hardware["miss_builds"],
                        "DONE": hardware["done_builds"],
                        "SKIP": hardware["skip_builds"],
                    },
                )
            )

        return hardwares

    def _get_results(
        self, start_date: datetime, end_date: datetime, origin: str
    ) -> HardwareResponse:
        hardware = self._get_tests_from_database(start_date, end_date, origin)

        return HardwareResponse(hardware=hardware)

    @extend_schema(
        parameters=[HardwareQueryParamsDocumentationOnly], responses=HardwareResponse
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

        try:
            result = self._get_results(start_date, end_date, origin)

            if len(result.hardware) < 1:
                return create_api_error_response(
                    error_message="No hardwares found", status_code=HTTPStatus.OK
                )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(data=result.model_dump(), status=HTTPStatus.OK)
