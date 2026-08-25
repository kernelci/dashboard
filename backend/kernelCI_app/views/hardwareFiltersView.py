from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.queries.hardware import get_hardware_filters
from kernelCI_app.typeModels.hardwareListing import (
    HardwareFiltersQueryParams,
    HardwareFiltersQueryParamsDocumentationOnly,
    HardwareFiltersResponse,
)


class HardwareFiltersView(APIView):
    @extend_schema(
        parameters=[HardwareFiltersQueryParamsDocumentationOnly],
        responses=HardwareFiltersResponse,
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
            start_date=query_params.start_date, end_date=query_params.end_date
        )
        result = HardwareFiltersResponse(**filters)

        return Response(data=result.model_dump(), status=HTTPStatus.OK)
