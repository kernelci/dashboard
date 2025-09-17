from kernelCI_app.tests.utils.client.treeClient import TreeClient
from kernelCI_app.tests.utils.asserts import (
    assert_status_code_and_error_response,
)
from kernelCI_app.utils import string_to_json
from http import HTTPStatus

import pytest

client = TreeClient()


@pytest.mark.parametrize(
    "tree_name, git_branch, query, has_error_body",
    [
        ("android", "android-mainline", {}, False),
        ("mainline", "master", {"origin": "microsoft"}, False),
        ("invalid_tree_name", "invalid_branch", {}, True),
        (
            "qcom",
            "for-next",
            {},
            False,
        ),  # No qcom tree in trees-name.yaml, only in kcidb
        (
            "agross",
            "for-next",
            {},
            True,
        ),  # No agross tree in kcidb, only in trees-name.yaml
        (
            "android",
            "android-mainline",
            {
                "origin": "maestro",
                "commit_hash": "1064be81d694bc2b3c308de6b2951c21a3f89677",
            },
            False,
        ),
        (
            "mainline",
            "master",
            {
                "origin": "microsoft",
                "commit_hash": "c4dce0c094a89b1bc8fde1163342bd6fe29c0370",
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
