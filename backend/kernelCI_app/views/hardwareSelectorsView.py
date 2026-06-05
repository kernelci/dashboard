from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.queries.hardware import get_hardware_selectors
from kernelCI_app.typeModels.hardwareSelectors import (
    HardwareSelectorBranch,
    HardwareSelectorRevision,
    HardwareSelectorsQueryParams,
    HardwareSelectorsQueryParamsDocumentationOnly,
    HardwareSelectorsResponse,
    HardwareSelectorTree,
)


class HardwareSelectorsView(APIView):
    def _sanitize_records(self, selectors_raw: list[dict]) -> HardwareSelectorsResponse:
        trees: list[dict] = []
        trees_by_name: dict[str, dict] = {}

        for row in selectors_raw:
            tree_name = row["tree_name"]
            tree = trees_by_name.get(tree_name)
            if tree is None:
                tree = {
                    "tree_name": tree_name,
                    "branches": [],
                    "_branches_by_key": {},
                }
                trees_by_name[tree_name] = tree
                trees.append(tree)

            branch_key = (row["git_repository_url"], row["git_repository_branch"])
            branch = tree["_branches_by_key"].get(branch_key)
            if branch is None:
                branch = {
                    "git_repository_url": row["git_repository_url"],
                    "git_repository_branch": row["git_repository_branch"],
                    "revisions": [],
                }
                tree["_branches_by_key"][branch_key] = branch
                tree["branches"].append(branch)

            branch["revisions"].append(
                {
                    "git_commit_hash": row["git_commit_hash"],
                    "git_commit_name": row["git_commit_name"],
                    "start_time": row["start_time"],
                }
            )

        sanitized_trees: list[HardwareSelectorTree] = []
        for tree in trees:
            branches = [
                HardwareSelectorBranch(
                    git_repository_url=branch["git_repository_url"],
                    git_repository_branch=branch["git_repository_branch"],
                    revisions=[
                        HardwareSelectorRevision(**revision)
                        for revision in branch["revisions"]
                    ],
                )
                for branch in tree["branches"]
            ]
            sanitized_trees.append(
                HardwareSelectorTree(
                    tree_name=tree["tree_name"],
                    branches=branches,
                )
            )

        return HardwareSelectorsResponse(trees=sanitized_trees)

    @extend_schema(
        parameters=[HardwareSelectorsQueryParamsDocumentationOnly],
        responses=HardwareSelectorsResponse,
    )
    def get(self, request: Request):
        try:
            query_params = HardwareSelectorsQueryParams(
                origin=request.GET.get("origin")
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        selectors_raw = get_hardware_selectors(origin=query_params.origin)

        try:
            result = self._sanitize_records(selectors_raw=selectors_raw)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(data=result.model_dump(), status=HTTPStatus.OK)
