import requests
from django.urls import reverse

from kernelCI_app.tests.utils.client.baseClient import BaseClient
from kernelCI_app.typeModels.testDetails import (
    TestStatusHistoryRequest,
    TestStatusSeriesRequest,
)


class TestClient(BaseClient):
    def get_test_details(self, *, test_id: str) -> requests.Response:
        path = reverse("testDetails", kwargs={"test_id": test_id})
        url = self.get_endpoint(path=path)
        return requests.get(url)

    def get_test_issues(self, *, test_id: str) -> requests.Response:
        path = reverse("testIssues", kwargs={"test_id": test_id})
        url = self.get_endpoint(path=path)
        return requests.get(url)

    def get_test_status_history(
        self,
        *,
        query: TestStatusHistoryRequest,
    ) -> requests.Response:
        path = reverse("testStatusHistory")
        url = self.get_endpoint(path=path, query=query.model_dump())
        return requests.get(url)

    def get_test_series(
        self,
        *,
        query: TestStatusSeriesRequest,
    ) -> requests.Response:
        path = reverse("TestStatusSeries")
        url = self.get_endpoint(path=path, query=query.model_dump())
        return requests.get(url)
