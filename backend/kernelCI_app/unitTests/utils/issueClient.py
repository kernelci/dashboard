import requests
from django.urls import reverse
import json
from kernelCI_app.unitTests.utils.baseClient import BaseClient

"""
    IssueDetailsBuildsView
    IssueDetailsTestsView
    IssueDetailsView
    IssueExtrasView
    IssueView
"""


class IssueClient(BaseClient):
    def get_issues_list(self, *, origin: str | None, interval_in_days: int | None):
        path = reverse("issue")
        query = {"origin": origin, "intervalInDays": interval_in_days}
        url = self.get_endpoint(path=path, query=query)
        return requests.get(url)

    def get_issues_details(self, *, issue_id, issue_version):
        path = reverse("issueDetails", kwargs={"issue_id": issue_id})
        query = None if issue_version is None else {"version": issue_version}
        url = self.get_endpoint(path=path, query=query)
        return requests.get(url)

    def get_issues_extra(self, issues_list):
        path = reverse("issueExtraDetails")
        url = self.get_endpoint(path=path)
        return requests.post(url=url, data=json.dumps({"issues": issues_list}))

    def get_issue_tests(self, issue_id, issue_version):
        path = reverse("issueDetailsTests", kwargs={"issue_id": issue_id})
        query = {"version": issue_version}
        url = self.get_endpoint(path=path, query=query)
        return requests.get(url)

    def get_issue_builds(self, issue_id, issue_version):
        path = reverse("issueDetailsBuilds", kwargs={"issue_id": issue_id})
        query = {"version": issue_version}
        url = self.get_endpoint(path=path, query=query)
        return requests.get(url)
