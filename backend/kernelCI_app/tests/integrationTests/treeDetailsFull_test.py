from kernelCI_app.tests.utils.client.treeClient import TreeClient
from kernelCI_app.tests.utils.asserts import assert_status_code_and_error_response
from kernelCI_app.utils import string_to_json
from kernelCI_app.tests.utils.commonTreeAsserts import (
    execute_boots_asserts,
    execute_builds_asserts,
    execute_summary_asserts,
    execute_tests_asserts,
)
from http import HTTPStatus
import pytest
from kernelCI_app.tests.utils.treeDetailsCommonTestCases import (
    ANDROID_MAESTRO_MAINLINE,
    NEXT_PENDING_FIXES_BROONIE,
    UNEXISTENT_TREE,
    INVALID_QUERY_PARAMS,
    BROONIE_MISC_BROONIE,
)


client = TreeClient()


@pytest.mark.parametrize(
    "base_tree, status_code, has_error_body",
    [
        (ANDROID_MAESTRO_MAINLINE, HTTPStatus.OK, False),
        (NEXT_PENDING_FIXES_BROONIE, HTTPStatus.OK, False),
        (UNEXISTENT_TREE, HTTPStatus.OK, True),
        (INVALID_QUERY_PARAMS, HTTPStatus.OK, True),
        (BROONIE_MISC_BROONIE, HTTPStatus.OK, False),
    ],
)
def test_tree_details_full(
    pytestconfig,
    base_tree: dict,
    status_code: HTTPStatus,
    has_error_body: bool,
) -> None:
    id, params, _ = base_tree.values()

    query = params["query"]
    filters = params.get("filters")

    response = client.get_tree_details_full(tree_id=id, query=query, filters=filters)
    content = string_to_json(response.content.decode())

    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=status_code,
        should_error=has_error_body,
    )

    if not has_error_body:
        execute_summary_asserts(content)
        execute_builds_asserts(pytestconfig, content, filters)
        execute_boots_asserts(pytestconfig, content, filters)
        execute_tests_asserts(pytestconfig, content, filters)
