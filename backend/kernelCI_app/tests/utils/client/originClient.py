from django.urls import reverse

import requests
from kernelCI_app.tests.utils.client.baseClient import BaseClient


class OriginClient(BaseClient):
    def get_origins(self) -> requests.Response:
        path = reverse("originsView")
        url = self.get_endpoint(path=path)
        return requests.get(url)
