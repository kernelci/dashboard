from http import HTTPStatus

import pytest

from kernelCI_app.tests.utils.asserts import (
    assert_status_code_and_error_response,
)
from kernelCI_app.tests.utils.client.treeClient import TreeClient
from kernelCI_app.utils import string_to_json

client = TreeClient()


@pytest.mark.parametrize(
    "tree_name, git_branch, query, has_error_body",
    [
        ("android", "android-mainline", {}, False),
        ("next", "pending-fixes", {"origin": "broonie"}, False),
        ("invalid_tree_name", "invalid_branch", {}, True),
        (
            "broonie-misc",
            "for-kernelci",
            {},
            False,
        ),
        (
            "agross",
            "for-next",
            {},
            True,
        ),
        (
            "android",
            "android-mainline",
            {
                "origin": "maestro",
                "commit_hash": "fdf4d20b86285d7b4d1c2d3349a1bd1bc41b24ba",
            },
            False,
        ),
        (
            "next",
            "pending-fixes",
            {
                "origin": "broonie",
                "commit_hash": "33040a50cdaec186c13ef3f7b9c9b668d8e32637",
            },
            False,
        ),
        ("android", "android-mainline", {"commit_hash": "wrong_hash"}, True),
        ("invalid_tree_name", "invalid_branch", {"commit_hash": "any_hash"}, True),
    ],
)
def test_tree_latest(tree_name, git_branch, query, has_error_body):
    response = client.get_tree_latest(
        tree_name=tree_name, git_branch=git_branch, query=query
    )
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=HTTPStatus.OK,
        should_error=has_error_body,
    )
    if not has_error_body:
        assert "error" not in content
        assert content["tree_name"] == tree_name
        assert content["git_repository_branch"] == git_branch
        assert content["origin"] == query.get("origin", "maestro")
        if "commit_hash" in query:
            assert content["git_commit_hash"] == query["commit_hash"]
