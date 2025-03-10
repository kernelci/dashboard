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
