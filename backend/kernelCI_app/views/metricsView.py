from http import HTTPStatus

from django.db.utils import DatabaseError
from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.queries.notifications import get_metrics_data
from kernelCI_app.typeModels.metrics import (
    MetricsQueryParameters,
    MetricsResponse,
    metrics_report_data_to_response,
)


class MetricsView(APIView):
    @extend_schema(
        parameters=[MetricsQueryParameters],
        responses={
            HTTPStatus.OK: MetricsResponse,
            HTTPStatus.BAD_REQUEST: dict[str, str],
        },
        methods=["GET"],
    )
    def get(self, request) -> Response:
        try:
            query_parameters = MetricsQueryParameters.model_validate(request.GET.dict())
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        if query_parameters.start_days_ago <= query_parameters.end_days_ago:
            return create_api_error_response(
                error_message=ClientStrings.METRICS_INVALID_INTERVAL
            )
        try:
            data = get_metrics_data(
                start_days_ago=query_parameters.start_days_ago,
                end_days_ago=query_parameters.end_days_ago,
            )
        except DatabaseError as e:
            return create_api_error_response(
                error_message=str(e),
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        try:
            valid_response = metrics_report_data_to_response(data)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
