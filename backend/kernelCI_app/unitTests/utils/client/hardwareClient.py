import requests
from django.urls import reverse
from kernelCI_app.unitTests.utils.client.baseClient import BaseClient
from kernelCI_app.typeModels.hardwareDetails import HardwareDetailsPostBody
from kernelCI_app.typeModels.hardwareListing import HardwareQueryParamsDocumentationOnly
import json


class HardwareClient(BaseClient):
    def get_hardware_listing(
        self, *, query: HardwareQueryParamsDocumentationOnly
    ) -> requests.Response:
        path = reverse("hardware")
        url = self.get_endpoint(path=path, query=query.model_dump())
        return requests.get(url)

    def post_hardware_boots(
        self, *, hardware_id: str, body: HardwareDetailsPostBody
    ) -> requests.Response:
        path = reverse("hardwareDetailsBoots", kwargs={"hardware_id": hardware_id})
        url = self.get_endpoint(path=path)
        return requests.post(url=url, data=json.dumps(body.model_dump()))

    def post_hardware_builds(
        self, *, hardware_id: str, body: HardwareDetailsPostBody
    ) -> requests.Response:
        path = reverse("hardwareDetailsBuilds", kwargs={"hardware_id": hardware_id})
        url = self.get_endpoint(path=path)
        return requests.post(url, data=json.dumps(body.model_dump()))

    def post_hardware_tests(
        self, *, hardware_id: str, body: HardwareDetailsPostBody
    ) -> requests.Response:
        path = reverse("hardwareDetailsTests", kwargs={"hardware_id": hardware_id})
        url = self.get_endpoint(path=path)
        return requests.post(url, data=json.dumps(body.model_dump()))

    def post_hardware_details_summary(
        self,
        *,
        hardware_id: str,
        body: HardwareDetailsPostBody,
    ) -> requests.Response:
        path = reverse("hardwareDetailsSummary", kwargs={"hardware_id": hardware_id})
        url = self.get_endpoint(path=path)
        return requests.post(url, data=json.dumps(body.model_dump()))

    def post_hardware_details_full(
        self,
        *,
        hardware_id: str,
        body: HardwareDetailsPostBody,
    ):
        path = reverse("hardwareDetails", kwargs={"hardware_id": hardware_id})
        url = self.get_endpoint(path=path)
        return requests.post(url, data=json.dumps(body.model_dump()))
