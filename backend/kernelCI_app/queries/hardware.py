import json
from kernelCI_app.helpers.environment import (
    get_schema_version,
    set_schema_version,
)
from kernelCI_app.helpers.logger import log_message
import typing_extensions
from datetime import datetime
from django.db import connection, models
from django.db.utils import ProgrammingError
from django.db.models import Subquery

from kernelCI_app.models import Tests
from kernelCI_app.helpers.trees import get_tree_heads
from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.helpers.build import (
    is_valid_does_not_exist_exception,
    valid_status_field,
)
from kernelCI_app.cache import get_query_cache, set_query_cache
from kernelCI_app.typeModels.hardwareDetails import Tree


@typing_extensions.deprecated(
    "This implementation is temporary while the schema is being updated."
)
def get_hardware_listing_data(
    start_date: datetime, end_date: datetime, origin: str
) -> list[dict]:
    try:
        if get_schema_version() != "5":
            return get_hardware_listing_valid(start_date, end_date, origin)
        return get_hardware_listing_status(start_date, end_date, origin)
    except ProgrammingError as e:
        if is_valid_does_not_exist_exception(e):
            set_schema_version(version="5")
            log_message("Hardware Listing -- Schema version updated to 5")
            return get_hardware_listing_status(start_date, end_date, origin)
        else:
            raise


@typing_extensions.deprecated(
    "This implementation is temporary while the schema is being updated."
)
def get_hardware_listing_valid(
    start_date: datetime, end_date: datetime, origin: str
) -> list[dict]:
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "origin": origin,
    }

    query = """
        WITH relevant_tests AS (
            SELECT
                "tests"."environment_compatible",
                "tests"."environment_misc",
                "tests"."status",
                "builds"."valid",
                "tests"."path",
                "tests"."build_id",
                "tests"."id"
            FROM
                "tests"
            INNER JOIN "builds" ON
                ("tests"."build_id" = "builds"."id")
            INNER JOIN "checkouts" ON
                ("builds"."checkout_id" = "checkouts"."id")
            WHERE
                (("tests"."environment_compatible" IS NOT NULL
                    OR ("tests"."environment_misc" -> 'platform') IS NOT NULL)
                    AND "checkouts"."git_commit_hash" IN (
                    SELECT
                        DISTINCT ON
                        (U0."tree_name",
                        U0."git_repository_branch",
                        U0."git_repository_url") U0."git_commit_hash"
                    FROM
                        "checkouts" U0
                    WHERE
                        (U0."origin" = %(origin)s
                            AND U0."start_time" >= %(start_date)s
                            AND U0."start_time" <= %(end_date)s)
                    ORDER BY
                        U0."tree_name" ASC,
                        U0."git_repository_branch" ASC,
                        U0."git_repository_url" ASC,
                        U0."start_time" DESC)
                    AND "checkouts"."origin" = %(origin)s
                    AND "tests"."start_time" >= %(start_date)s
                    AND "tests"."start_time" <= %(end_date)s)
            )
            SELECT
                hardware,
                ARRAY_AGG(DISTINCT platform) AS platform,
                COUNT(DISTINCT CASE WHEN "valid" = TRUE AND build_id
                                NOT LIKE 'maestro:dummy_%%' THEN build_id END) AS pass_builds,
                COUNT(DISTINCT CASE WHEN "valid" = FALSE AND build_id
                                NOT LIKE 'maestro:dummy_%%' THEN build_id END) AS fail_builds,
                COUNT(DISTINCT CASE WHEN "valid" IS NULL AND build_id IS
                                NOT NULL AND build_id NOT LIKE 'maestro:dummy_%%' THEN build_id END)
                                AS null_builds,
                0 AS error_builds,
                0 AS miss_builds,
                0 AS done_builds,
                0 AS skip_builds,
                COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                                AND "status" = 'FAIL' THEN 1 END) AS fail_tests,
                COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                                AND "status" = 'ERROR' THEN 1 END) AS error_tests,
                COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                                AND "status" = 'MISS' THEN 1 END) AS miss_tests,
                COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                                AND "status" = 'PASS' THEN 1 END) AS pass_tests,
                COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                                AND "status" = 'DONE' THEN 1 END) AS done_tests,
                COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                                AND "status" = 'SKIP' THEN 1 END) AS skip_tests,
                SUM(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                                AND "status" IS NULL AND id IS NOT NULL THEN 1 ELSE 0 END) AS null_tests,
                COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                                AND "status" = 'FAIL' THEN 1 END) AS fail_boots,
                COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                                AND "status" = 'ERROR' THEN 1 END) AS error_boots,
                COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                                AND "status" = 'MISS' THEN 1 END) AS miss_boots,
                COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                                AND "status" = 'PASS' THEN 1 END) AS pass_boots,
                COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                                AND "status" = 'DONE' THEN 1 END) AS done_boots,
                COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                                AND "status" = 'SKIP' THEN 1 END) AS skip_boots,
                SUM(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                                AND "status" IS NULL AND id IS NOT NULL THEN 1 ELSE 0 END) AS null_boots
            FROM
                (
                SELECT
                    UNNEST("environment_compatible") AS hardware,
                    "environment_misc" ->> 'platform' AS platform,
                    build_id,
                    "valid",
                    "path",
                    status,
                    id
                FROM
                    relevant_tests
                WHERE
                    "environment_compatible" IS NOT NULL
            UNION
                SELECT
                    "environment_misc" ->> 'platform' AS hardware,
                    "environment_misc" ->> 'platform' AS platform,
                    build_id,
                    "valid",
                    "path",
                    status,
                    id
                FROM
                    relevant_tests
                WHERE
                    "environment_misc" ->> 'platform' IS NOT NULL
                    AND environment_compatible IS NULL
            ) AS combined_data
        GROUP BY
    hardware;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return dict_fetchall(cursor)


@typing_extensions.deprecated(
    "This implementation is temporary while the schema is being updated."
)
def get_hardware_listing_status(
    start_date: datetime, end_date: datetime, origin: str
) -> list[dict]:
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "origin": origin,
    }

    # TODO: Check if this status count is correct
    query = """
        WITH relevant_tests AS (
            SELECT
                "tests"."environment_compatible",
                "tests"."environment_misc",
                "tests"."status" AS test_status,
                "builds"."status" AS build_status,
                "tests"."path",
                "tests"."build_id",
                "tests"."id"
            FROM
                "tests"
            INNER JOIN "builds" ON
                ("tests"."build_id" = "builds"."id")
            INNER JOIN "checkouts" ON
                ("builds"."checkout_id" = "checkouts"."id")
            WHERE
                (("tests"."environment_compatible" IS NOT NULL
                    OR ("tests"."environment_misc" -> 'platform') IS NOT NULL)
                    AND "checkouts"."git_commit_hash" IN (
                    SELECT
                        DISTINCT ON
                        (U0."tree_name",
                        U0."git_repository_branch",
                        U0."git_repository_url") U0."git_commit_hash"
                    FROM
                        "checkouts" U0
                    WHERE
                        (U0."origin" = %(origin)s
                            AND U0."start_time" >= %(start_date)s
                            AND U0."start_time" <= %(end_date)s)
                    ORDER BY
                        U0."tree_name" ASC,
                        U0."git_repository_branch" ASC,
                        U0."git_repository_url" ASC,
                        U0."start_time" DESC)
                    AND "checkouts"."origin" = %(origin)s
                    AND "tests"."start_time" >= %(start_date)s
                    AND "tests"."start_time" <= %(end_date)s)
            )
            SELECT
                hardware,
                ARRAY_AGG(DISTINCT platform) AS platform,
                COUNT(DISTINCT CASE WHEN "build_status" = 'PASS' AND build_id
                                NOT LIKE 'maestro:dummy_%%' THEN build_id END) AS pass_builds,
                COUNT(DISTINCT CASE WHEN "build_status" = 'FAIL' AND build_id
                                NOT LIKE 'maestro:dummy_%%' THEN build_id END) AS fail_builds,
                COUNT(DISTINCT CASE WHEN "build_status" IS NULL AND build_id IS
                                NOT NULL AND build_id NOT LIKE 'maestro:dummy_%%' THEN build_id END)
                                AS null_builds,
                COUNT(DISTINCT CASE WHEN "build_status" = 'ERROR' AND build_id
                                NOT LIKE 'maestro:dummy_%%' THEN build_id END) AS error_builds,
                COUNT(DISTINCT CASE WHEN "build_status" = 'MISS' AND build_id
                                NOT LIKE 'maestro:dummy_%%' THEN build_id END) AS miss_builds,
                COUNT(DISTINCT CASE WHEN "build_status" = 'DONE' AND build_id
                                NOT LIKE 'maestro:dummy_%%' THEN build_id END) AS done_builds,
                COUNT(DISTINCT CASE WHEN "build_status" = 'SKIP' AND build_id
                                NOT LIKE 'maestro:dummy_%%' THEN build_id END) AS skip_builds,
                COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                                AND "test_status" = 'FAIL' THEN 1 END) AS fail_tests,
                COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                                AND "test_status" = 'ERROR' THEN 1 END) AS error_tests,
                COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                                AND "test_status" = 'MISS' THEN 1 END) AS miss_tests,
                COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                                AND "test_status" = 'PASS' THEN 1 END) AS pass_tests,
                COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                                AND "test_status" = 'DONE' THEN 1 END) AS done_tests,
                COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                                AND "test_status" = 'SKIP' THEN 1 END) AS skip_tests,
                SUM(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                                AND "test_status" IS NULL AND id IS NOT NULL THEN 1 ELSE 0 END) AS null_tests,
                COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                                AND "test_status" = 'FAIL' THEN 1 END) AS fail_boots,
                COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                                AND "test_status" = 'ERROR' THEN 1 END) AS error_boots,
                COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                                AND "test_status" = 'MISS' THEN 1 END) AS miss_boots,
                COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                                AND "test_status" = 'PASS' THEN 1 END) AS pass_boots,
                COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                                AND "test_status" = 'DONE' THEN 1 END) AS done_boots,
                COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                                AND "test_status" = 'SKIP' THEN 1 END) AS skip_boots,
                SUM(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                                AND "test_status" IS NULL AND id IS NOT NULL THEN 1 ELSE 0 END) AS null_boots
            FROM
                (
                SELECT
                    UNNEST("environment_compatible") AS hardware,
                    "environment_misc" ->> 'platform' AS platform,
                    build_id,
                    build_status,
                    "path",
                    test_status,
                    id
                FROM
                    relevant_tests
                WHERE
                    "environment_compatible" IS NOT NULL
            UNION
                SELECT
                    "environment_misc" ->> 'platform' AS hardware,
                    "environment_misc" ->> 'platform' AS platform,
                    build_id,
                    build_status,
                    "path",
                    test_status,
                    id
                FROM
                    relevant_tests
                WHERE
                    "environment_misc" ->> 'platform' IS NOT NULL
                    AND environment_compatible IS NULL
            ) AS combined_data
        GROUP BY
    hardware;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return dict_fetchall(cursor)


def get_hardware_details_data(
    *,
    hardware_id: str,
    origin: str,
    trees_with_selected_commits: list[Tree],
    start_datetime: datetime,
    end_datetime: datetime,
):
    cache_key = "hardwareDetailsFullData"

    tests_cache_params = {
        "hardware_id": hardware_id,
        "origin": origin,
        "trees": trees_with_selected_commits,
        "start_date": start_datetime,
        "end_date": end_datetime,
    }

    records = get_query_cache(cache_key, tests_cache_params)

    if not records:
        records = query_records(
            hardware_id=hardware_id,
            origin=origin,
            trees=trees_with_selected_commits,
            start_date=start_datetime,
            end_date=end_datetime,
        )
        set_query_cache(cache_key, tests_cache_params, records)

    return records


@typing_extensions.deprecated(
    "This implementation is temporary while the schema is being updated."
)
def query_records(
    *, hardware_id: str, origin: str, trees: list[Tree], start_date: int, end_date: int
) -> list[dict] | None:
    commit_hashes = [tree.head_git_commit_hash for tree in trees]

    # TODO Treat commit_hash collision (it can happen between repos)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    tests.id,
                    tests.environment_misc,
                    tests.path,
                    tests.comment,
                    tests.log_url,
                    tests.status,
                    tests.start_time,
                    tests.duration,
                    tests.misc,
                    tests.build_id,
                    tests.environment_compatible,
                    builds.architecture AS build__architecture,
                    builds.config_name AS build__config_name,
                    builds.misc AS build__misc,
                    builds.config_url AS build__config_url,
                    builds.compiler AS build__compiler,
                    builds.{0} AS build__status,
                    builds.duration AS build__duration,
                    builds.log_url AS build__log_url,
                    builds.start_time AS build__start_time,
                    checkouts.git_repository_url AS build__checkout__git_repository_url,
                    checkouts.git_repository_branch AS build__checkout__git_repository_branch,
                    checkouts.git_commit_name AS build__checkout__git_commit_name,
                    checkouts.git_commit_hash AS build__checkout__git_commit_hash,
                    checkouts.tree_name AS build__checkout__tree_name,
                    incidents.id AS incidents__id,
                    incidents.issue_id AS incidents__issue__id,
                    issues.version AS incidents__issue__version,
                    issues.comment AS incidents__issue__comment,
                    issues.report_url AS incidents__issue__report_url,
                    incidents.test_id AS incidents__test_id,
                    T7.issue_id AS build__incidents__issue__id,
                    T8.version AS build__incidents__issue__version
                FROM
                    tests
                INNER JOIN builds ON
                    tests.build_id = builds.id
                INNER JOIN checkouts ON
                    builds.checkout_id = checkouts.id
                LEFT OUTER JOIN incidents ON
                    tests.id = incidents.test_id
                LEFT OUTER JOIN issues ON
                    incidents.issue_id = issues.id AND incidents.issue_version = issues.version
                LEFT OUTER JOIN incidents T7 ON
                    builds.id = T7.build_id
                LEFT OUTER JOIN issues T8 ON
                    T7.issue_id = T8.id AND T7.issue_version = T8.version
                WHERE
                    (
                        tests.environment_compatible @> ARRAY[%s]::TEXT[]
                        OR tests.environment_misc ->> 'platform' = %s
                    )
                    AND checkouts.origin = %s
                    AND tests.start_time >= %s
                    AND tests.start_time <= %s
                    AND checkouts.git_commit_hash IN ({1})
                ORDER BY
                    issues."_timestamp" DESC
                """.format(
                    valid_status_field(), ",".join(["%s"] * len(commit_hashes))
                ),
                [
                    hardware_id,
                    hardware_id,
                    origin,
                    start_date,
                    end_date,
                ]
                + commit_hashes,
            )

            return dict_fetchall(cursor)
    except ProgrammingError as e:
        if is_valid_does_not_exist_exception(e):
            set_schema_version(version="5")
            log_message("Hardware Details -- Schema version updated to 5")
        else:
            raise


def get_hardware_trees_data(
    *,
    hardware_id: str,
    origin: str,
    selected_commits: dict[str, str],
    start_datetime: datetime,
    end_datetime: datetime,
) -> list[Tree]:
    cache_key = "hardwareDetailsTreeData"

    trees_cache_params = {
        "hardware_id": hardware_id,
        "origin": origin,
        "selected_commits": json.dumps(selected_commits),
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
    }

    trees: list[Tree] = get_query_cache(cache_key, trees_cache_params)

    if not trees:
        # We need a subquery because if we filter by any hardware, it will get the
        # last head that has that hardware, but not the real head of the trees
        trees_subquery = get_tree_heads(origin, start_datetime, end_datetime)

        tree_id_fields = [
            "build__checkout__tree_name",
            "build__checkout__git_repository_branch",
            "build__checkout__git_repository_url",
        ]

        trees_query_set = (
            Tests.objects.filter(
                models.Q(environment_compatible__contains=[hardware_id])
                | models.Q(environment_misc__platform=hardware_id),
                origin=origin,
                build__checkout__start_time__lte=end_datetime,
                build__checkout__start_time__gte=start_datetime,
                build__checkout__git_commit_hash__in=Subquery(trees_subquery),
            )
            .values(
                *tree_id_fields,
                "build__checkout__git_commit_name",
                "build__checkout__git_commit_hash",
                "build__checkout__git_commit_tags",
            )
            .distinct(
                *tree_id_fields,
                "build__checkout__git_commit_hash",
            )
            .order_by(
                *tree_id_fields,
                "build__checkout__git_commit_hash",
                "-build__checkout__start_time",
            )
        )

        trees = []
        for idx, tree in enumerate(trees_query_set):
            trees.append(
                Tree(
                    index=str(idx),
                    tree_name=tree["build__checkout__tree_name"],
                    git_repository_branch=tree[
                        "build__checkout__git_repository_branch"
                    ],
                    git_repository_url=tree["build__checkout__git_repository_url"],
                    head_git_commit_name=tree["build__checkout__git_commit_name"],
                    head_git_commit_hash=tree["build__checkout__git_commit_hash"],
                    head_git_commit_tag=tree["build__checkout__git_commit_tags"],
                    selected_commit_status=None,
                    is_selected=None,
                )
            )

        set_query_cache(cache_key, trees_cache_params, trees)

    return trees
