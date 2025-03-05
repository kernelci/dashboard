from http import HTTPStatus
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.typeModels.buildDetails import BuildDetailsResponse
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from pydantic import ValidationError
from kernelCI_app.queries.build import get_build_details


class BuildDetails(APIView):
    @extend_schema(responses=BuildDetailsResponse)
    def get(self, request, build_id: str) -> Response:
        records = get_build_details(build_id)

        # Temporary during schema transition
        if records is None:
            message = (
                "This error was probably caused because the server was using"
                "an old version of the database. Please try requesting again"
            )
            return create_api_error_response(
                error_message=message,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        if not records:
            return create_api_error_response(
                error_message="Build not found",
                status_code=HTTPStatus.OK,
            )

        try:
            valid_response = BuildDetailsResponse(**records[0])
        except ValidationError as e:
            return Response(
                data=e.json(),
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        return Response(valid_response.model_dump())
