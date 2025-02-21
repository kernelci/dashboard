import pytest
from http import HTTPStatus

from kernelCI_app.utils import string_to_json
from kernelCI_app.unitTests.utils.healthCheck import online
from kernelCI_app.unitTests.utils.treeClient import TreeClient
from kernelCI_app.typeModels.treeDetails import TreeQueryParameters


INVALID_TREE = {
    "id": "invalid_id",
    "query": TreeQueryParameters(origin="", git_url="", git_branch=""),
}
MAINLINE_MASTER_TREE = {
    "id": "8a61cb6e150ea907b580a1b5e705decb0a3ffc86",
    "query": TreeQueryParameters(
        origin="maestro",
        git_url="https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
        git_branch="master",
    ),
}


@online
@pytest.mark.parametrize(
    "base_tree, status_code, has_error_body",
    [
        (
            INVALID_TREE,
            HTTPStatus.OK,
            True,
        ),
        (
            MAINLINE_MASTER_TREE,
            HTTPStatus.OK,
            False,
        ),
    ],
)
def test_no_filters(base_tree, status_code, has_error_body):
    tree_id = base_tree["id"]
    query = base_tree["query"]
    client = TreeClient()
    response = client.get_tree_details_summary(tree_id=tree_id, query=query)
    content = string_to_json(response.content.decode())
    assert response.status_code == status_code
    if has_error_body:
        assert "error" in content


@online
@pytest.mark.parametrize(
    "base_tree, filters",
    [
        (
            MAINLINE_MASTER_TREE,
            {"boot.status": "FAIL"},
        ),
    ],
)
def test_test_status_filter(base_tree, filters):
    """
    Tests for the status filter for both boots and tests
    (couldn't add build to the same test function because it has a different nomenclature).
    This test only for when 1 status is being passed to the filter
    """
    tree_id = base_tree["id"]
    query = base_tree["query"]
    client = TreeClient()
    response = client.get_tree_details_summary(
        tree_id=tree_id, query=query, filters=filters
    )
    content = string_to_json(response.content.decode())
    assert response.status_code == HTTPStatus.OK
    assert "error" not in content

    # filter field = 'boot' | 'test' and response field = 'boots' | 'tests'
    field, _ = list(filters.keys())[0].split(".")
    value = list(filters.values())[0]
    field = field + "s"

    assert "summary" in content
    assert field in content["summary"]
    assert "status" in content["summary"][field]
    for status, count in content["summary"][field]["status"].items():
        if status != value:
            assert count == 0

    assert "architectures" in content["summary"][field]
    for arch in content["summary"][field]["architectures"]:
        for status, count in arch["status"].items():
            if status != value:
                assert count == 0

    assert "configs" in content["summary"][field]
    for config in content["summary"][field]["configs"].values():
        for status, count in config.items():
            if status != value:
                assert count == 0
