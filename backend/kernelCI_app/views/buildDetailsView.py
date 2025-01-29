from querybuilder.query import Query
from kernelCI_app.models import Builds
from http import HTTPStatus
from kernelCI_app.typeModels.buildDetails import BuildDetailsResponse
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from pydantic import ValidationError


class BuildDetails(APIView):
    @extend_schema(responses=BuildDetailsResponse)
    def get(self, request, build_id: str) -> Response:
        build_fields = [
            "id",
            "_timestamp",
            "checkout_id",
            "origin",
            "comment",
            "start_time",
            "log_excerpt",
            "duration",
            "architecture",
            "command",
            "compiler",
            "config_name",
            "config_url",
            "log_url",
            "valid",
            "misc",
            "input_files",
            "output_files",
        ]

        query = Query().from_table(Builds, build_fields)
        query.join(
            "checkouts",
            join_type="LEFT JOIN",
            fields=[
                "tree_name",
                "git_repository_branch",
                "git_commit_name",
                "git_repository_url",
                "git_commit_hash",
                "git_commit_tags",
            ],
            condition="checkouts.id = builds.checkout_id",
        )
        query.where(**{"builds.id__eq": build_id})

        records = query.select()
        if not records:
            return Response(data={"error": "Build not found"}, status=HTTPStatus.OK)

        try:
            valid_response = BuildDetailsResponse(**records[0])
        except ValidationError as e:
            return Response(
                data=e.json(),
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        return Response(valid_response.model_dump())
