from django.db import connection
from datetime import datetime
from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.helpers.errorHandling import (
    create_api_error_response,
)
from kernelCI_app.constants.general import UNKNOWN_STRING
from kernelCI_app.typeModels.hardwareListing import (
    HardwareItem,
    HardwareQueryParams,
    HardwareQueryParamsDocumentationOnly,
    HardwareResponse,
)


class HardwareView(APIView):
    def _get_tests_from_database(
        self, start_date: datetime, end_date: datetime, origin: str
    ) -> list[HardwareItem]:
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
                                    NOT LIKE 'maestro:dummy_%%' THEN build_id END) AS valid_builds,
                    COUNT(DISTINCT CASE WHEN "valid" = FALSE AND build_id
                                    NOT LIKE 'maestro:dummy_%%' THEN build_id END) AS invalid_builds,
                    COUNT(DISTINCT CASE WHEN "valid" IS NULL AND build_id IS
                                    NOT NULL AND build_id NOT LIKE 'maestro:dummy_%%' THEN build_id END)
                                    AS null_builds,
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
        hardwares: list[HardwareItem] = []
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            hardwares_raw = dict_fetchall(cursor)

            # TODO Move this logic to the pydantic model
            for hardware in hardwares_raw:
                platform = ""
                match len(hardware["platform"]):
                    case 0:
                        platform = UNKNOWN_STRING
                    case 1:
                        platform = hardware["platform"][0]
                    case _:
                        platform = hardware["platform"]

                hardwares.append(
                    HardwareItem(
                        hardware_name=hardware["hardware"],
                        platform=platform,
                        test_status_summary={
                            "FAIL": hardware["fail_tests"],
                            "ERROR": hardware["error_tests"],
                            "MISS": hardware["miss_tests"],
                            "PASS": hardware["pass_tests"],
                            "DONE": hardware["done_tests"],
                            "SKIP": hardware["skip_tests"],
                            "NULL": hardware["null_tests"],
                        },
                        boot_status_summary={
                            "FAIL": hardware["fail_boots"],
                            "ERROR": hardware["error_boots"],
                            "MISS": hardware["miss_boots"],
                            "PASS": hardware["pass_boots"],
                            "DONE": hardware["done_boots"],
                            "SKIP": hardware["skip_boots"],
                            "NULL": hardware["null_boots"],
                        },
                        build_status_summary={
                            "valid": hardware["valid_builds"],
                            "invalid": hardware["invalid_builds"],
                            "null": hardware["null_builds"],
                        },
                    )
                )

        return hardwares

    def _get_results(
        self, start_date: datetime, end_date: datetime, origin: str
    ) -> HardwareResponse:
        hardware = self._get_tests_from_database(start_date, end_date, origin)

        return HardwareResponse(hardware=hardware)

    @extend_schema(
        parameters=[HardwareQueryParamsDocumentationOnly], responses=HardwareResponse
    )
    def get(self, request: Request):
        try:
            query_params = HardwareQueryParams(
                start_date=request.GET.get("startTimestampInSeconds"),
                end_date=request.GET.get("endTimeStampInSeconds"),
                origin=request.GET.get("origin"),
            )

            start_date: datetime = query_params.start_date
            end_date: datetime = query_params.end_date
            origin = query_params.origin
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        try:
            result = self._get_results(start_date, end_date, origin)

            if len(result.hardware) < 1:
                return create_api_error_response(
                    error_message="No hardwares found", status_code=HTTPStatus.OK
                )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(data=result.model_dump(), status=HTTPStatus.OK)
