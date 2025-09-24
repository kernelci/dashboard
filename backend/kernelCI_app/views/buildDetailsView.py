from http import HTTPStatus
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.typeModels.buildDetails import BuildDetailsResponse
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from pydantic import ValidationError
from kernelCI_app.queries.build import get_build_details
from kernelCI_app.typeModels.commonOpenApiParameters import BUILD_ID_PATH_PARAM
from kernelCI_app.constants.localization import ClientStrings


class BuildDetails(APIView):
    @extend_schema(
        parameters=[BUILD_ID_PATH_PARAM],
        responses=BuildDetailsResponse,
    )
    def get(self, _request, build_id: str) -> Response:
        records = get_build_details(build_id)

        if not records:
            return create_api_error_response(
                error_message=ClientStrings.BUILD_DETAILS_NOT_FOUND,
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
