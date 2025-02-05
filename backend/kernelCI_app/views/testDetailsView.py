from http import HTTPStatus
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.models import Tests
from kernelCI_app.typeModels.testDetails import TestDetailsResponse
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from pydantic import ValidationError


class TestDetails(APIView):
    @extend_schema(
        responses=TestDetailsResponse,
    )
    def get(self, _request, test_id: str) -> Response:
        fields = [
            "id",
            "build_id",
            "status",
            "path",
            "log_excerpt",
            "log_url",
            "misc",
            "environment_misc",
            "start_time",
            "environment_compatible",
            "output_files",
            "build__compiler",
            "build__architecture",
            "build__config_name",
            "build__checkout__git_commit_hash",
            "build__checkout__git_repository_branch",
            "build__checkout__git_repository_url",
            "build__checkout__git_commit_tags",
            "build__checkout__tree_name",
        ]

        response = Tests.objects.filter(id=test_id).values(*fields).first()

        if response is None:
            return create_api_error_response(
                error_message="Test not found", status_code=HTTPStatus.OK
            )

        try:
            valid_response = TestDetailsResponse(**response)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
