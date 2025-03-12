from kernelCI_app.unitTests.utils.healthCheck import online
from kernelCI_app.unitTests.utils.client.treeClient import TreeClient
from kernelCI_app.unitTests.utils.asserts import (
    assert_status_code_and_error_response,
    assert_has_fields_in_response_content,
    assert_build_filters,
)
from kernelCI_app.utils import string_to_json
from kernelCI_app.unitTests.utils.fields.tree import tree_builds_expected_fields
from http import HTTPStatus
import pytest
from kernelCI_app.unitTests.utils.treeDetailsCommonTestCases import (
    ANDROID_MAESTRO_MAINLINE,
    NEXT_PENDING_FIXES_BROONIE,
    UNEXISTENT_TREE,
    INVALID_QUERY_PARAMS,
)

client = TreeClient()


@online
@pytest.mark.parametrize(
    "base_tree, status_code, has_error_body",
    [
        (ANDROID_MAESTRO_MAINLINE, HTTPStatus.OK, False),
        (NEXT_PENDING_FIXES_BROONIE, HTTPStatus.OK, False),
        (UNEXISTENT_TREE, HTTPStatus.OK, True),
        (INVALID_QUERY_PARAMS, HTTPStatus.OK, True),
    ],
)
def test_tree_details_build(
    pytestconfig,
    base_tree: dict,
    status_code: HTTPStatus,
    has_error_body: bool,
) -> None:
    id, params = base_tree.values()

    query = params["query"]
    filters = params.get("filters")

    response = client.get_tree_details_builds(tree_id=id, query=query, filters=filters)
    content = string_to_json(response.content.decode())

    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=status_code,
        should_error=has_error_body,
    )

    if not has_error_body:
        assert "builds" in content

        if "builds" in content:
            first_build = content["builds"][0]

            assert_has_fields_in_response_content(
                fields=tree_builds_expected_fields, response_content=first_build
            )

            assert_build_filters(filters=filters, build=first_build)

            if pytestconfig.getoption("--run-all") and len(content["builds"]) > 1:
                for build in content["builds"][1:]:
                    assert_has_fields_in_response_content(
                        fields=tree_builds_expected_fields, response_content=build
                    )

                    assert_build_filters(filters=filters, build=build)
