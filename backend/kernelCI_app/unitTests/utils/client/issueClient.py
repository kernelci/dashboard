import requests
from django.urls import reverse
import json
from kernelCI_app.unitTests.utils.client.baseClient import BaseClient


class IssueClient(BaseClient):
    def get_issues_list(
        self, *, origin: str | None, interval_in_days: int | None
    ) -> requests.Response:
        path = reverse("issue")
        query = {"origin": origin, "intervalInDays": interval_in_days}
        url = self.get_endpoint(path=path, query=query)
        return requests.get(url)

    def get_issues_details(
        self, *, issue_id: str, issue_version: int | None
    ) -> requests.Response:
        path = reverse("issueDetails", kwargs={"issue_id": issue_id})
        query = {"version": issue_version}
        url = self.get_endpoint(path=path, query=query)
        return requests.get(url)

    def get_issues_extra(
        self, *, issues_list: list[tuple[str, int | None]]
    ) -> requests.Response:
        path = reverse("issueExtraDetails")
        url = self.get_endpoint(path=path)
        return requests.post(url=url, data=json.dumps({"issues": issues_list}))

    def _get_issues_resources(
        self, *, viewname: str, issue_id: str, issue_version: int | None
    ) -> requests.Response:
        path = reverse(viewname, kwargs={"issue_id": issue_id})
        query = {"version": issue_version}
        url = self.get_endpoint(path=path, query=query)
        return requests.get(url)

    def get_issue_tests(
        self, *, issue_id: str, issue_version: int | None
    ) -> requests.Response:
        return self._get_issues_resources(
            viewname="issueDetailsTests", issue_id=issue_id, issue_version=issue_version
        )

    def get_issue_builds(
        self, *, issue_id: str, issue_version: int | None
    ) -> requests.Response:
        return self._get_issues_resources(
            viewname="issueDetailsBuilds",
            issue_id=issue_id,
            issue_version=issue_version,
        )
