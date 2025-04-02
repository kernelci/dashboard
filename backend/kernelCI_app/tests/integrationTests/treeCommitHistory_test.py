import pytest
from http import HTTPStatus
from requests import Response
from kernelCI_app.tests.utils.client.treeClient import TreeClient
from kernelCI_app.tests.utils.asserts import assert_status_code_and_error_response
from kernelCI_app.tests.utils.commonTreeAsserts import (
    assert_tree_commit_history_fields,
)
from kernelCI_app.utils import string_to_json


client = TreeClient()


# https://dashboard.kernelci.org/tree/a1c24ab822793eb513351686f631bd18952b7870?p=bt&tf%7Cb=a&tf%7Cbt=f&tf%7Ct=i&ti%7Cc=v6.14-rc3-18-ga1c24ab822793&ti%7Cch=a1c24ab822793eb513351686f631bd18952b7870&ti%7Cgb=for-kernelci&ti%7Cgu=https%3A%2F%2Fgit.kernel.org%2Fpub%2Fscm%2Flinux%2Fkernel%2Fgit%2Farm64%2Flinux.git&ti%7Ct=arm64
ARM64_TREE = {
    "id": "a1c24ab822793eb513351686f631bd18952b7870",
    "query": {
        "origin": "maestro",
        "git_url": "https://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux.git",
        "git_branch": "for-kernelci",
    },
}


def request_data(base_tree: dict, filters: dict | None = None) -> tuple[Response, dict]:
    tree_id = base_tree["id"]
    query = base_tree["query"]
    response = client.get_tree_commit_history(
        tree_id=tree_id, query=query, filters=filters
    )
    content = string_to_json(response.content.decode())
    return response, content


@pytest.mark.parametrize(
    "tree, status_code, has_error_body",
    [
        ({"id": "invalid_id", "query": {"origin": "maestro"}}, HTTPStatus.OK, True),
        ({"id": ARM64_TREE["id"], "query": {}}, HTTPStatus.BAD_REQUEST, True),
        (ARM64_TREE, HTTPStatus.OK, False),
    ],
)
def test_no_filters(
    pytestconfig, tree: dict, status_code: HTTPStatus, has_error_body: bool
) -> None:
    response, content = request_data(tree)
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=status_code,
        should_error=has_error_body,
    )

    if not has_error_body:
        assert_tree_commit_history_fields(content[0])

    if pytestconfig.getoption("--run-all") and len(content) > 1:
        for tree in content[1:]:
            assert_tree_commit_history_fields(tree)


@pytest.mark.parametrize(
    "tree, filters",
    [
        (ARM64_TREE, {"boot.status": "FAIL"}),
        (ARM64_TREE, {"test.status": "PASS"}),
        (ARM64_TREE, {"build.status": "FAIL"}),
        (ARM64_TREE, {"build.status": "PASS"}),
    ],
)
def test_status_filter(pytestconfig, tree: dict, filters: dict) -> None:
    response, content = request_data(tree, filters)
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=HTTPStatus.OK,
        should_error=False,
    )

    # filter task = 'boot' | 'test' and response task = 'boots' | 'tests'
    task, _ = list(filters.items())[0]
    task = task.split(".")[0] + "s"
    filter_value = list(filters.values())[0]

    content_list = content if pytestconfig.getoption("--run-all") else content[:1]

    for commit_history in content_list:
        for field, value in commit_history[task].items():
            if field.lower() != filter_value.lower():
                assert value == 0
