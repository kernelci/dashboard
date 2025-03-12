from kernelCI_app.unitTests.utils.healthCheck import online
from kernelCI_app.unitTests.utils.client.treeClient import TreeClient
from kernelCI_app.unitTests.utils.asserts import (
    assert_status_code_and_error_response,
    assert_has_fields_in_response_content,
    assert_build_filters,
    assert_boots_filters,
    assert_tests_filters,
)
from kernelCI_app.utils import string_to_json
from kernelCI_app.unitTests.utils.fields import tree
from http import HTTPStatus
import pytest
from kernelCI_app.unitTests.utils.treeDetailsCommonTestCases import (
    ANDROID_MAESTRO_MAINLINE,
    NEXT_PENDING_FIXES_BROONIE,
    UNEXISTENT_TREE,
    INVALID_QUERY_PARAMS,
    BROONIE_MISC_BROONIE,
)


client = TreeClient()


def execute_builds_asserts(pytestconfig, content: dict, filters: dict):
    assert "builds" in content
    if "builds" in content and len(content["builds"]) > 0:
        first_build = content["builds"][0]

        assert_has_fields_in_response_content(
            fields=tree.tree_builds_expected_fields, response_content=first_build
        )

        assert_build_filters(filters=filters, build=first_build)

        if pytestconfig.getoption("--run-all") and len(content["builds"]) > 1:
            for build in content["builds"][1:]:
                assert_has_fields_in_response_content(
                    fields=tree.tree_builds_expected_fields, response_content=build
                )

                assert_build_filters(filters=filters, build=build)


def execute_boots_asserts(pytestconfig, content: dict, filters: dict):
    assert "boots" in content
    if "boots" in content and len(content["boots"]) > 0:
        first_boot = content["boots"][0]

        assert_has_fields_in_response_content(
            fields=tree.tree_tests_expected_fields, response_content=first_boot
        )

        assert_boots_filters(filters=filters, boot=first_boot)

        if pytestconfig.getoption("--run-all") and len(content["boots"]) > 1:
            for boot in content["boots"][1:]:
                assert_has_fields_in_response_content(
                    fields=tree.tree_tests_expected_fields, response_content=boot
                )

                assert_boots_filters(filters=filters, boot=boot)


def execute_tests_asserts(pytestconfig, content: dict, filters: dict):
    assert "tests" in content
    if "tests" in content and len(content["tests"]) > 0:
        first_test = content["tests"][0]

        assert_has_fields_in_response_content(
            fields=tree.tree_tests_expected_fields, response_content=first_test
        )

        assert_tests_filters(filters=filters, test=first_test)

        if pytestconfig.getoption("--run-all") and len(content["tests"]) > 1:
            for test in content["tests"][1:]:
                assert_has_fields_in_response_content(
                    fields=tree.tree_tests_expected_fields, response_content=test
                )

                assert_tests_filters(filters=filters, test=test)


def execute_summary_asserts(content: dict):
    assert "summary" in content
    assert "common" in content
    assert "filters" in content
    assert_has_fields_in_response_content(
        fields=tree.tree_summary, response_content=content
    )
    assert_has_fields_in_response_content(
        fields=tree.tree_summary_summary, response_content=content["summary"]
    )
    assert_has_fields_in_response_content(
        fields=tree.tree_summary_common, response_content=content["common"]
    )
    assert_has_fields_in_response_content(
        fields=tree.tree_summary_filters, response_content=content["filters"]
    )
    assert_has_fields_in_response_content(
        fields=tree.tree_test_summary, response_content=content["summary"]["tests"]
    )
    assert_has_fields_in_response_content(
        fields=tree.tree_test_summary, response_content=content["summary"]["boots"]
    )
    assert_has_fields_in_response_content(
        fields=tree.tree_build_summary,
        response_content=content["summary"]["builds"],
    )


@online
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
    id, params = base_tree.values()

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
