from http import HTTPStatus

from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.treeCompare import (
    _HashAccumulator,
    build_compare_response,
    change_counts_from_row,
    process_build_rows,
    process_rollup_rows,
)
from kernelCI_app.queries.tree import (
    get_tree_compare_boots_change_counts,
    get_tree_compare_builds,
    get_tree_compare_builds_change_counts,
    get_tree_compare_rollup,
    get_tree_compare_tests_change_counts,
)
from kernelCI_app.typeModels.commonOpenApiParameters import (
    GIT_BRANCH_PATH_PARAM,
    TREE_NAME_PATH_PARAM,
)
from kernelCI_app.typeModels.treeCompare import (
    TreeCompareQueryParameters,
    TreeCompareResponse,
)


class TreeCompareView(APIView):
    def _merge_accumulators(
        self,
        *,
        target: dict[str, _HashAccumulator],
        builds_data: dict[str, _HashAccumulator],
        boots_tests_data: dict[str, _HashAccumulator],
    ) -> None:
        for commit_hash, build_acc in builds_data.items():
            target_acc = target.setdefault(commit_hash, _HashAccumulator())
            target_acc.builds = build_acc.builds

        for commit_hash, entity_acc in boots_tests_data.items():
            target_acc = target.setdefault(commit_hash, _HashAccumulator())
            target_acc.boots = entity_acc.boots
            target_acc.tests = entity_acc.tests

    @extend_schema(
        parameters=[
            TREE_NAME_PATH_PARAM,
            GIT_BRANCH_PATH_PARAM,
            TreeCompareQueryParameters,
        ],
        responses=TreeCompareResponse,
    )
    def get(
        self,
        request: HttpRequest,
        tree_name: str,
        git_branch: str,
    ) -> Response:
        try:
            query_params = TreeCompareQueryParameters(
                hash_a=request.GET.get("hash_a", ""),
                hash_b=request.GET.get("hash_b", ""),
                origin=request.GET.get("origin", DEFAULT_ORIGIN),
            )
        except ValidationError as error:
            return Response(data=error.json(), status=HTTPStatus.BAD_REQUEST)

        if not query_params.hash_a or not query_params.hash_b:
            return create_api_error_response(
                status_code=HTTPStatus.BAD_REQUEST,
                error_message="hash_a and hash_b are required",
            )

        commit_hashes = [query_params.hash_a, query_params.hash_b]
        query_kwargs = {
            "commit_hashes": commit_hashes,
            "origin_param": query_params.origin,
            "git_branch_param": git_branch,
            "tree_name": tree_name,
        }
        change_kwargs = {
            "hash_a": query_params.hash_a,
            "hash_b": query_params.hash_b,
            "origin_param": query_params.origin,
            "git_branch_param": git_branch,
            "tree_name": tree_name,
        }

        build_rows = get_tree_compare_builds(**query_kwargs)
        builds_data = process_build_rows(
            rows=build_rows,
            commit_hashes=commit_hashes,
        )
        boots_tests_data = process_rollup_rows(
            rows=get_tree_compare_rollup(**query_kwargs),
            commit_hashes=commit_hashes,
        )

        accumulators = {
            commit_hash: _HashAccumulator() for commit_hash in commit_hashes
        }
        self._merge_accumulators(
            target=accumulators,
            builds_data=builds_data,
            boots_tests_data=boots_tests_data,
        )

        changes = {
            "builds": change_counts_from_row(
                get_tree_compare_builds_change_counts(**change_kwargs)
            ),
            "boots": change_counts_from_row(
                get_tree_compare_boots_change_counts(**change_kwargs)
            ),
            "tests": change_counts_from_row(
                get_tree_compare_tests_change_counts(**change_kwargs)
            ),
        }

        git_url = ""
        if build_rows:
            git_url = build_rows[0].get("git_repository_url") or ""

        response = build_compare_response(
            hash_a=query_params.hash_a,
            hash_b=query_params.hash_b,
            tree_name=tree_name,
            branch=git_branch,
            git_url=git_url,
            accumulators=accumulators,
            changes=changes,
        )

        return Response(
            data=response.model_dump(by_alias=True),
            status=HTTPStatus.OK,
        )
