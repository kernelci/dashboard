from typing import Optional
from querybuilder.query import Query
from kernelCI_app.models import Builds, Tests


def get_build_details(build_id: str) -> Optional[list[dict]]:
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
        {"valid": "status"},
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

    return query.select()


def get_build_tests(build_id: str) -> Optional[list[dict]]:
    result = Tests.objects.filter(build_id=build_id).values(
        "id",
        "duration",
        "status",
        "path",
        "start_time",
        "environment_compatible",
        "environment_misc",
        "build__status",
    )
    return list(result)
