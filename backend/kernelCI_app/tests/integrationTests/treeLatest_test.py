from kernelCI_app.tests.utils.client.treeClient import TreeClient
from kernelCI_app.tests.utils.asserts import (
    assert_status_code_and_error_response,
)
from kernelCI_app.utils import string_to_json
from http import HTTPStatus

import pytest

client = TreeClient()


@pytest.mark.parametrize(
    "tree_name, branch, query, has_error_body",
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
            False,
        ),  # No agross tree in kcidb, only in trees-name.yaml
        (
            "android",
            "android-mainline",
            {
                "origin": "maestro",
                "git_commit_hash": "1064be81d694bc2b3c308de6b2951c21a3f89677",
            },
            False,
        ),
    ],
)
def test_tree_latest(tree_name, branch, query, has_error_body):
    response = client.get_tree_latest(tree_name=tree_name, branch=branch, query=query)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=HTTPStatus.OK,
        should_error=has_error_body,
    )
