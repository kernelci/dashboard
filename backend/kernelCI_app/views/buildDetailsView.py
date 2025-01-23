from django.http import JsonResponse
from django.views import View
from querybuilder.query import Query
from kernelCI_app.models import Builds
from http import HTTPStatus
from kernelCI_app.helpers.errorHandling import create_error_response


class BuildDetails(View):

    def get(self, request, build_id):
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
            "output_files"
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
            return create_error_response(
                error_message="Build not found", status_code=HTTPStatus.OK
            )

        return JsonResponse(records[0])
