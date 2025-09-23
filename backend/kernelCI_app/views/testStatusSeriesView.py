from http import HTTPStatus
from django.db import ProgrammingError
from django.http import HttpRequest
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.test import process_test_status_history
from kernelCI_app.queries.test import get_series_data
from kernelCI_app.typeModels.testDetails import (
    TestStatusSeriesRequest,
    TestStatusSeriesResponse,
)
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from pydantic import ValidationError
from kernelCI_app.constants.localization import ClientStrings
import hashlib


class TestStatusSeries(APIView):
    @extend_schema(
        parameters=[TestStatusSeriesRequest],
        request=TestStatusSeriesRequest,
        responses=TestStatusSeriesResponse,
    )
    def get(self, request: HttpRequest) -> Response:
        try:
            params = TestStatusSeriesRequest.model_validate(request.GET.dict())
            # The encoding on the database side retrieves the platform with quotes
            # because it is within a JSONB field
            if params.platform is not None and not (
                params.platform.startswith('"') and params.platform.endswith('"')
            ):
                params.platform = f'"{params.platform}"'

            test_key = "".join(filter(None, [params.path, params.platform]))
            test_series = hashlib.md5((test_key).encode("utf-8")).hexdigest()

            build_key = "".join(
                filter(None, [params.config_name, params.compiler, params.architecture])
            )
            build_series = hashlib.md5((build_key).encode("utf-8")).hexdigest()

            data = get_series_data(
                test_series=test_series,
                build_series=build_series,
                limit=params.group_size,
                origin=params.origin,
            )
        except ValidationError as e:
            return create_api_error_response(error_message=str(e))
        except ProgrammingError as e:
            # This happens when the view is accessed before the migrations are run
            # Status 501 might not be the most appropriate status code, but this
            # should not happen for long
            return Response(data={"warning": str(e)}, status=HTTPStatus.NOT_IMPLEMENTED)
        except Exception as e:
            return create_api_error_response(
                error_message=str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR
            )

        if len(data) == 0:
            return create_api_error_response(
                error_message=ClientStrings.TEST_SERIES_NOT_FOUND,
                status_code=HTTPStatus.OK,
            )

        regression_type = process_test_status_history(status_history=data)

        try:
            valid_response = TestStatusSeriesResponse(
                status_history=data,
                regression_type=regression_type,
                test_series=test_series,
                build_series=build_series,
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
