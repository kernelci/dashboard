from http import HTTPStatus
from typing import Dict, Optional
from urllib.parse import urlencode
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import JsonResponse
from django.urls import reverse
from pydantic import ValidationError

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.models import Checkouts
from kernelCI_app.typeModels.treeDetails import (
    TreeLatestPathParameters,
    TreeLatestResponse,
    TreeLatestQueryParameters,
)


class TreeLatest(APIView):
    def _fetch_latest_tree(
        self, tree_name: str, branch: str, origin: str
    ) -> Optional[Dict]:
        tree_fields = [
            "git_commit_hash",
            "git_commit_name",
            "git_repository_url",
        ]

        query = (
            Checkouts.objects.values(*tree_fields)
            .filter(
                origin=origin,
                tree_name=tree_name,
                git_repository_branch=branch,
                git_commit_hash__isnull=False,
            )
            .order_by("-field_timestamp")
            .first()
        )

        return query

    @extend_schema(
        responses=TreeLatestResponse,
        parameters=[TreeLatestQueryParameters],
        methods=["GET"],
    )
    def get(self, request, tree_name: str, branch: str) -> JsonResponse:
        try:
            parsed_params = TreeLatestPathParameters(tree_name=tree_name, branch=branch)
        except ValidationError as e:
            return Response(data=e.json, status=HTTPStatus.BAD_REQUEST)

        tree_not_found_error_message = "Tree not found."
        origin = request.GET.get("origin")
        if origin is None:
            origin = DEFAULT_ORIGIN
            tree_not_found_error_message += (
                f" No origin was provided so it was defaulted to {DEFAULT_ORIGIN}"
            )

        tree_data = self._fetch_latest_tree(
            tree_name=parsed_params.tree_name,
            branch=parsed_params.branch,
            origin=origin,
        )

        if tree_data is None:
            return create_api_error_response(
                error_message=tree_not_found_error_message,
                status_code=HTTPStatus.OK,
            )

        base_url = reverse(
            "treeDetailsView",
            kwargs={"commit_hash": tree_data["git_commit_hash"]},
        )

        # TODO: Newer versions of django added (or will add) a parameter to `reverse`
        # to pass the query parameters directly to it.
        # You can see more here: https://github.com/django/django/pull/18848
        # and here: https://code.djangoproject.com/ticket/25582#no1
        query_params = {
            "origin": origin,
            "git_url": tree_data["git_repository_url"],
            "git_branch": branch,
        }
        query_string = f"?{urlencode(query_params)}"

        response_data = {**tree_data, "api_url": f"{base_url}{query_string}"}

        try:
            valid_response = TreeLatestResponse(**response_data)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
