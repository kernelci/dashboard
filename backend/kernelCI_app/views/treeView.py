from typing import Dict
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from kernelCI_app.typeModels.commonListing import ListingQueryParameters
from kernelCI_app.utils import getQueryTimeInterval
from kernelCI_app.helpers.errorHandling import (
    create_api_error_response,
)
from http import HTTPStatus
from kernelCI_app.typeModels.treeListing import (
    TreeListingResponse,
)
from pydantic import ValidationError
from django.db import connection


class TreeView(APIView):
    def _sanitize_tree(self, checkout: Dict) -> Dict:
        build_status = {
            "valid": checkout[8],
            "invalid": checkout[9],
            "null": checkout[10],
        }

        test_status = {
            "fail": checkout[11],
            "error": checkout[12],
            "miss": checkout[13],
            "pass": checkout[14],
            "done": checkout[15],
            "skip": checkout[16],
            "null": checkout[17],
        }

        boot_status = {
            "fail": checkout[18],
            "error": checkout[19],
            "miss": checkout[20],
            "pass": checkout[21],
            "done": checkout[22],
            "skip": checkout[23],
            "null": checkout[24],
        }

        return {
            "git_repository_branch": checkout[2],
            "git_repository_url": checkout[3],
            "git_commit_hash": checkout[4],
            "git_commit_tags": checkout[5],
            "git_commit_name": checkout[6],
            "start_time": checkout[7],
            "build_status": {**build_status},
            "test_status": {**test_status},
            "boot_status": {**boot_status},
            "tree_names": checkout[25],
        }

    @extend_schema(
        responses=TreeListingResponse,
        parameters=[ListingQueryParameters],
        methods=["GET"],
    )
    def get(self, request) -> Response:
        try:
            request_params = ListingQueryParameters(
                origin=request.GET.get("origin"),
                interval_in_days=request.GET.get("intervalInDays"),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        origin_param = request_params.origin
        interval_days = request_params.interval_in_days

        interval_days_data = {"days": interval_days}

        params = {
            "origin_param": origin_param,
            "interval_param": getQueryTimeInterval(**interval_days_data).timestamp(),
        }

        # '1 as id' is necessary in this case because django raw queries must include the primary key.
        # In this case we don't need the primary key and adding it would alter the GROUP BY clause,
        # potentially causing the tree listing page show the same tree multiple times
        query = """
            SELECT
                1 as id,
                checkouts.tree_name,
                checkouts.git_repository_branch,
                checkouts.git_repository_url,
                checkouts.git_commit_hash,
                CASE
                    WHEN COUNT(DISTINCT checkouts.git_commit_tags) > 0 THEN
                    COALESCE(
                        ARRAY_AGG(DISTINCT checkouts.git_commit_tags) FILTER (
                            WHERE checkouts.git_commit_tags IS NOT NULL
                            AND checkouts.git_commit_tags::TEXT <> '{}'
                        ),
                        ARRAY[]::TEXT[]
                    )
                    ELSE ARRAY[]::TEXT[]
                END AS git_commit_tags,
                MAX(checkouts.git_commit_name) AS git_commit_name,
                MAX(checkouts.start_time) AS start_time,
                COUNT(DISTINCT CASE WHEN (builds.valid = true AND builds.id NOT LIKE 'maestro:dummy_%%')
                    THEN builds.id END) AS valid_builds,
                COUNT(DISTINCT CASE WHEN (builds.valid = false AND builds.id NOT LIKE 'maestro:dummy_%%')
                    THEN builds.id END) AS invalid_builds,
                COUNT(DISTINCT CASE WHEN (builds.valid IS NULL AND builds.id IS NOT NULL
                    AND builds.id NOT LIKE 'maestro:dummy_%%') THEN builds.id END) AS null_builds,
                COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
                    AND tests.status = 'FAIL' THEN 1 END) AS fail_tests,
                COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
                    AND tests.status = 'ERROR' THEN 1 END) AS error_tests,
                COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
                    AND tests.status = 'MISS' THEN 1 END) AS miss_tests,
                COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
                    AND tests.status = 'PASS' THEN 1 END) AS pass_tests,
                COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
                    AND tests.status = 'DONE' THEN 1 END) AS done_tests,
                COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
                    AND tests.status = 'SKIP' THEN 1 END) AS skip_tests,
                SUM(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
                    AND tests.status IS NULL AND tests.id IS NOT NULL THEN 1 ELSE 0 END) AS null_tests,
                COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
                    AND tests.status = 'FAIL' THEN 1 END) AS fail_boots,
                COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
                    AND tests.status = 'ERROR' THEN 1 END) AS error_boots,
                COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
                    AND tests.status = 'MISS' THEN 1 END) AS miss_boots,
                COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
                    AND tests.status = 'PASS' THEN 1 END) AS pass_boots,
                COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
                    AND tests.status = 'DONE' THEN 1 END) AS done_boots,
                COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
                    AND tests.status = 'SKIP' THEN 1 END) AS skip_boots,
                SUM(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
                    AND tests.status IS NULL AND tests.id IS NOT NULL THEN 1 ELSE 0 END) AS null_boots,
                COALESCE(
                    ARRAY_AGG(DISTINCT tree_name) FILTER (
                        WHERE tree_name IS NOT NULL
                    ),
                    ARRAY[]::TEXT[]
                ) AS tree_names
            FROM
                checkouts
            LEFT JOIN
                builds ON builds.checkout_id = checkouts.id
            LEFT JOIN
                tests ON tests.build_id = builds.id
            WHERE
                checkouts.git_commit_hash IN (
                    SELECT
                        git_commit_hash
                    FROM
                        (
                            SELECT
                                git_repository_branch,
                                git_repository_url,
                                git_commit_hash,
                                ROW_NUMBER() OVER (
                                    PARTITION BY git_repository_url, git_repository_branch
                                    ORDER BY start_time DESC
                                ) AS time_order
                            FROM
                                checkouts
                            WHERE
                                origin = %(origin_param)s
                                AND start_time >= TO_TIMESTAMP(%(interval_param)s)
                        ) AS ordered_checkouts_by_tree
                    WHERE
                        time_order = 1
                    ORDER BY
                        git_repository_branch,
                        git_repository_url,
                        time_order
                )
                AND checkouts.origin = %(origin_param)s
            GROUP BY
                checkouts.git_commit_hash,
                checkouts.git_repository_branch,
                checkouts.git_repository_url,
                checkouts.tree_name
            ORDER BY
                checkouts.git_commit_hash;
            ;
            """

        checkouts = {}
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            checkouts = cursor.fetchall()

        if not checkouts:
            return create_api_error_response(
                error_message="Trees not found", status_code=HTTPStatus.OK
            )

        checkouts = [self._sanitize_tree(checkout) for checkout in checkouts]

        try:
            valid_response = TreeListingResponse(checkouts)
        except ValidationError as e:
            return create_api_error_response(
                error_message=e.json(), status_code=HTTPStatus.INTERNAL_SERVER_ERROR
            )

        return Response(valid_response.model_dump(by_alias=True))
