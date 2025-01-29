from http import HTTPStatus
from kernelCI_app.typeModels.buildDetails import BuildTestsResponse
from kernelCI_app.models import Tests
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from pydantic import ValidationError


class BuildTests(APIView):
    @extend_schema(responses=BuildTestsResponse)
    def get(self, request, build_id: str) -> Response:
        result = Tests.objects.filter(build_id=build_id).values(
            "id", "duration", "status", "path", "start_time", "environment_compatible"
        )

        if not result:
            return Response(
                data={"error": "No tests found for this build"},
                status=HTTPStatus.OK,
            )

        try:
            valid_response = BuildTestsResponse(result)
        except ValidationError as e:
            return Response(
                data=e.json(),
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        return Response(valid_response.model_dump())
