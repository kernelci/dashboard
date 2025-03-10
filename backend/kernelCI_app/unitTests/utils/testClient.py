import requests
from django.urls import reverse

from kernelCI_app.typeModels.testDetails import TestStatusHistoryRequest
from kernelCI_app.unitTests.utils.baseClient import BaseClient


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
        path = reverse("testStatusHistory", args={})
        url = self.get_endpoint(path=path, query=query.model_dump())
        return requests.get(url)
