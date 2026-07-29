from http import HTTPStatus

from kernelCI_app.tests.utils.client.treeClient import TreeClient
from kernelCI_app.utils import string_to_json

client = TreeClient()

# Seeded in tree_data.py (issue1460_*): same git_url/branch/commit hash, different tree_name.
ORIGIN = "maestro"
GIT_URL = "https://example.com/kernelci-dashboard-issue-1460.git"
GIT_BRANCH = "issue-1460-branch"
OLDER_TREE_NAME = "issue1460_older"
NEWER_TREE_NAME = "issue1460_newer"


def test_tree_report_returns_requested_tree_name():
    response = client.get_tree_report(
        query={
            "origin": ORIGIN,
            "git_url": GIT_URL,
            "git_branch": GIT_BRANCH,
            "tree_name": OLDER_TREE_NAME,
        }
    )
    assert response.status_code == HTTPStatus.OK
    content = string_to_json(response.content.decode())

    assert f"/tree/{OLDER_TREE_NAME}/" in content["dashboard_url"]
    assert NEWER_TREE_NAME not in content["dashboard_url"]
