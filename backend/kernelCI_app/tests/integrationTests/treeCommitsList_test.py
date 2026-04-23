from http import HTTPStatus

import pytest

from kernelCI_app.tests.utils.asserts import assert_status_code_and_error_response
from kernelCI_app.tests.utils.client.treeClient import TreeClient
from kernelCI_app.utils import string_to_json
from requests import Response

client = TreeClient()


def request_data(tree_name: str, git_branch: str, query: dict) -> tuple[Response, dict]:
    response = client.get_tree_commits_list(
        tree_name=tree_name, git_branch=git_branch, query=query
    )
    content = string_to_json(response.content.decode())
    return response, content


@pytest.mark.parametrize(
    "tree_name, git_branch, query, status_code, has_error_body",
    [
        (
            "fluster_mainline",
            "master",
            {
                "origin": "maestro",
                "git_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
            },
            HTTPStatus.OK,
            False,
        ),
        (
            "nonexistent",
            "master",
            {
                "origin": "maestro",
                "git_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
            },
            HTTPStatus.OK,
            True,
        ),
    ],
)
def test_tree_commits_list_view(
    tree_name: str,
    git_branch: str,
    query: dict,
    status_code: HTTPStatus,
    has_error_body: bool,
) -> None:
    response, content = request_data(tree_name, git_branch, query)
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=status_code,
        should_error=has_error_body,
    )

    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=HTTPStatus.OK,
        should_error=False,
    )
