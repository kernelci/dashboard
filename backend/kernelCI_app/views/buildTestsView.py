from http import HTTPStatus
from kernelCI_app.helpers.build import build_status_map, valid_status_field
from kernelCI_app.helpers.discordWebhook import send_discord_notification
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.logger import create_endpoint_notification
from kernelCI_app.queries.build import get_build_tests
from kernelCI_app.typeModels.buildDetails import BuildTestsResponse
from drf_spectacular.utils import extend_schema
from kernelCI_app.typeModels.databases import FAIL_STATUS
from rest_framework.views import APIView
from rest_framework.response import Response
from pydantic import ValidationError


class BuildTests(APIView):
    @extend_schema(responses=BuildTestsResponse)
    def get(self, request, build_id: str) -> Response:
        result = get_build_tests(build_id)

        # Temporary during schema transition
        if result is None:
            message = (
                "This error was probably caused because the server was using"
                "an old version of the database. Please try requesting again"
            )
            return create_api_error_response(
                error_message=message,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        if not result:
            return Response(
                data={"error": "No tests found for this build"},
                status=HTTPStatus.OK,
            )

        if (
            build_status_map(result[0].get(f"build__{valid_status_field()}"))
            == FAIL_STATUS
        ):
            notification = create_endpoint_notification(
                message="Found tests for a failed build.",
                request=request,
            )
            send_discord_notification(content=notification)

        try:
            valid_response = BuildTestsResponse(result)
        except ValidationError as e:
            return Response(
                data=e.json(),
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        return Response(valid_response.model_dump())
