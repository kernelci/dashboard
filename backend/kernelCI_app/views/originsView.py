from http import HTTPStatus
from kernelCI_app.helpers.errorHandling import create_api_error_response
from rest_framework.views import APIView
from rest_framework.response import Response
from kernelCI_app.queries.checkout import get_origins
from drf_spectacular.utils import extend_schema


class OriginsView(APIView):
    @extend_schema(
        responses={HTTPStatus.OK: list[str], HTTPStatus.BAD_REQUEST: dict[str, str]},
        methods=["GET"],
    )
    def get(self, _request) -> Response:
        origins = get_origins()
        if len(origins) == 0:
            return create_api_error_response(error_message="No origins found")

        return Response(origins)
