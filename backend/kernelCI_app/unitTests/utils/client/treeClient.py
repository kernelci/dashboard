from typing import Any
import requests
from django.urls import reverse
from kernelCI_app.helpers.filters import FilterFields
from kernelCI_app.typeModels.treeDetails import TreeQueryParameters
from kernelCI_app.unitTests.utils.client.baseClient import BaseClient


class TreeClient(BaseClient):
    def get_tree_listing_fast(self, *, query: dict) -> requests.Response:
        path = reverse("tree-fast")
        url = self.get_endpoint(path=path, query=query)
        return requests.get(url)

    def get_tree_listing(self, *, query: dict) -> requests.Response:
        path = reverse("tree")
        url = self.get_endpoint(path=path, query=query)
        return requests.get(url)

    def get_tree_latest(
        self, *, tree_name: str, branch: str, query: dict
    ) -> requests.Response:
        path = reverse("treeLatest", kwargs={"tree_name": tree_name, "branch": branch})
        url = self.get_endpoint(path=path, query=query)
        return requests.get(url)

    def get_tree_details_summary(
        self,
        *,
        tree_id: str,
        query: TreeQueryParameters,
        filters: dict[FilterFields, Any] | None = None,
    ) -> requests.Response:
        path = reverse("treeDetailsSummaryView", kwargs={"commit_hash": tree_id})
        url = self.get_endpoint(path=path, query=query.model_dump(), filters=filters)
        return requests.get(url)

    def get_tree_commit_history(
        self,
        *,
        tree_id: str,
        query: dict,
        filters: dict[FilterFields, Any] | None = None,
    ) -> requests.Response:
        path = reverse("treeCommits", kwargs={"commit_hash": tree_id})
        url = self.get_endpoint(path=path, query=query, filters=filters)
        return requests.get(url)

    def get_tree_details_full(
        self,
        *,
        tree_id: str,
        query: TreeQueryParameters,
        filters: dict[FilterFields, Any] | None = None,
    ) -> requests.Response:
        path = reverse("treeDetailsView", kwargs={"commit_hash": tree_id})
        url = self.get_endpoint(path=path, query=query.model_dump(), filters=filters)
        return requests.get(url)

    def get_tree_details_builds(
        self,
        *,
        tree_id: str,
        query: TreeQueryParameters,
        filters: dict[FilterFields, Any] | None = None,
    ) -> requests.Response:
        path = reverse("treeDetailsBuildsView", kwargs={"commit_hash": tree_id})
        url = self.get_endpoint(path=path, query=query.model_dump(), filters=filters)
        return requests.get(url)

    def get_tree_details_boots(
        self,
        *,
        tree_id: str,
        query: TreeQueryParameters,
        filters: dict[FilterFields, Any] | None = None,
    ) -> requests.Response:
        path = reverse("treeDetailsBootsView", kwargs={"commit_hash": tree_id})
        url = self.get_endpoint(path=path, query=query.model_dump(), filters=filters)
        return requests.get(url)
