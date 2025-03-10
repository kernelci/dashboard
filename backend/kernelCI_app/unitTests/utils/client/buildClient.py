import requests
from django.urls import reverse

from kernelCI_app.unitTests.utils.client.baseClient import BaseClient


class BuildClient(BaseClient):
    def get_build_details(self, *, build_id: str) -> requests.Response:
        path = reverse("buildDetails", kwargs={"build_id": build_id})
        url = self.get_endpoint(path=path)
        return requests.get(url)

    # TODO: Implement this method for testing BuildTestsView
    def get_build_tests(self, *, build_id: str) -> requests.Response | Exception:
        pass
