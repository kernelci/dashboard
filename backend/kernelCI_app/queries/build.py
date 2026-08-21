import json
from typing import Optional

from django.db import connections
from querybuilder.query import Query

from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.models import Builds


def get_build_details(build_id: str) -> Optional[list[dict]]:
    build_fields = [
        "id",
        "_timestamp",
        "checkout_id",
        "origin as build_origin",
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
        "status",
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
            "origin",
        ],
        condition="checkouts.id = builds.checkout_id",
    )
    query.where(**{"builds.id__eq": build_id})

    return query.select()


def get_build_tests(build_id: str) -> Optional[list[dict]]:
    query = """
        SELECT
            tests.id,
            tests.duration,
            tests.status,
            tests.path,
            tests.start_time,
            tests.environment_compatible,
            tests.environment_misc,
            builds.status AS build__status,
            -- TODO remove misc->>'runtime' fallback after lab backfill
            COALESCE(labs.name, tests.misc->>'runtime') AS lab
        FROM tests
        INNER JOIN builds ON tests.build_id = builds.id
        LEFT JOIN labs ON tests.lab_id = labs.id
        WHERE tests.build_id = %s
    """
    with connections["default"].cursor() as cursor:
        cursor.execute(query, [build_id])
        rows = dict_fetchall(cursor)

    for row in rows:
        if isinstance(row["environment_misc"], str):
            row["environment_misc"] = json.loads(row["environment_misc"])
    return rows
