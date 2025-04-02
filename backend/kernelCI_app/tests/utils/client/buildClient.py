import requests
from django.urls import reverse

from kernelCI_app.tests.utils.client.baseClient import BaseClient


class BuildClient(BaseClient):
    def get_build_details(self, *, build_id: str) -> requests.Response:
        path = reverse("buildDetails", kwargs={"build_id": build_id})
        url = self.get_endpoint(path=path)
        return requests.get(url)

    def get_build_tests(self, *, build_id: str) -> requests.Response:
        path = reverse("buildTests", kwargs={"build_id": build_id})
        url = self.get_endpoint(path=path)
        return requests.get(url)

    def get_build_issues(self, *, build_id: str) -> requests.Response:
        path = reverse("buildIssues", kwargs={"build_id": build_id})
        url = self.get_endpoint(path=path)
        return requests.get(url)
