from typing import Any, Optional

from django.urls import reverse

import requests
from kernelCI_app.tests.utils.client.baseClient import BaseClient


class MetricsClient(BaseClient):
    def get_metrics(
        self, *, query: Optional[dict[str, Any]] = None
    ) -> requests.Response:
        path = reverse("metricsView")
        url = self.get_endpoint(path=path, query=query)
        return requests.get(url)
