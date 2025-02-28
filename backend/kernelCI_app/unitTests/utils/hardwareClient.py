import requests
from django.urls import reverse
from kernelCI_app.unitTests.utils.baseClient import BaseClient
from kernelCI_app.typeModels.hardwareDetails import HardwareDetailsPostBody
import json


class HardwareClient(BaseClient):
    def get_hardware_boots(
        self, *, hardware_id: str, body: HardwareDetailsPostBody
    ) -> requests.Response:
        path = reverse("hardwareDetailsBoots", kwargs={"hardware_id": hardware_id})
        url = self.get_endpoint(path=path)
        return requests.post(url=url, data=json.dumps(body.model_dump()))

    def get_hardware_builds(
        self, *, hardware_id: str, body: HardwareDetailsPostBody
    ) -> requests.Response:
        path = reverse("hardwareDetailsBuilds", kwargs={"hardware_id": hardware_id})
        url = self.get_endpoint(path=path)
        return requests.post(url, data=json.dumps(body.model_dump()))

    def get_hardware_tests(
        self, *, hardware_id: str, body: HardwareDetailsPostBody
    ) -> requests.Response:
        path = reverse("hardwareDetailsTests", kwargs={"hardware_id": hardware_id})
        url = self.get_endpoint(path=path)
        return requests.post(url, data=json.dumps(body.model_dump()))
