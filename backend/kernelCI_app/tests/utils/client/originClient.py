import requests
from django.urls import reverse

from kernelCI_app.tests.utils.client.baseClient import BaseClient


class OriginClient(BaseClient):
    def get_origins(self) -> requests.Response:
        path = reverse("originsView")
        url = self.get_endpoint(path=path)
        return requests.get(url)
