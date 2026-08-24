from django.urls import reverse

import requests
from kernelCI_app.tests.utils.client.baseClient import BaseClient


class LabOriginsClient(BaseClient):
    def get_lab_origins(self) -> requests.Response:
        path = reverse("labOriginsView")
        url = self.get_endpoint(path=path)
        return requests.get(url)
