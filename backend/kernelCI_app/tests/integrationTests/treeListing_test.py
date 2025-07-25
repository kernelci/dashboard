from kernelCI_app.tests.utils.client.treeClient import TreeClient
from kernelCI_app.tests.utils.asserts import (
    assert_status_code_and_error_response,
    assert_has_fields_in_response_content,
)
from kernelCI_app.utils import string_to_json
from kernelCI_app.tests.utils.fields.tree import (
    tree_fast,
    tree_listing,
    tree_listing_test_status,
    tree_listing_build_status,
)
from http import HTTPStatus

client = TreeClient()


def pytest_generate_tests(metafunc):
    tree_listing_base_cases = [
        (
            {"origin": "maestro", "interval_in_days": "7"},
            HTTPStatus.OK,
            False,
        ),
        (
            {"origin": "invalid", "interval_in_days": "7"},
            HTTPStatus.OK,
            True,
        ),
        (
            {"origin": "maestro", "interval_in_days": "-3"},
            HTTPStatus.BAD_REQUEST,
            True,
        ),
    ]

    tree_listing_extra_cases = []
    if metafunc.config.getoption("--run-all"):
        tree_listing_extra_cases += [
            (
                {"origin": "maestro", "interval_in_days": "0"},
                HTTPStatus.BAD_REQUEST,
                True,
            ),
            (
                {"origin": "redhat", "interval_in_days": "6"},
                HTTPStatus.OK,
                False,
            ),
            (
                {"origin": "microsoft", "interval_in_days": "5"},
                HTTPStatus.OK,
                False,
            ),
            (
                {"origin": "broonie", "interval_in_days": "4"},
                HTTPStatus.OK,
                False,
            ),
            (
                {"origin": "linaro", "interval_in_days": "7"},
                HTTPStatus.OK,
                False,
            ),
            (
                {"origin": "0dayci", "interval_in_days": "7"},
                HTTPStatus.OK,
                False,
            ),
            (
                {"origin": "syzbot", "interval_in_days": "7"},
                HTTPStatus.OK,
                False,
            ),
        ]

    if "tree_listing_input" in metafunc.fixturenames:
        metafunc.parametrize(
            "tree_listing_input", tree_listing_base_cases + tree_listing_extra_cases
        )


def test_tree_listing_fast(
    pytestconfig,
    tree_listing_input,
) -> None:
    query, status_code, has_error_body = tree_listing_input
    response = client.get_tree_listing_fast(query=query)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=status_code,
        should_error=has_error_body,
    )

    if not has_error_body:
        assert_has_fields_in_response_content(
            fields=tree_fast,
            response_content=content[0],
        )

        if pytestconfig.getoption("--run-all") and len(content) > 1:
            for tree in content[1:]:
                assert_has_fields_in_response_content(
                    fields=tree_fast,
                    response_content=tree,
                )


def test_tree_listing(
    pytestconfig,
    tree_listing_input,
) -> None:
    query, status_code, has_error_body = tree_listing_input
    response = client.get_tree_listing(query=query)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=status_code,
        should_error=has_error_body,
    )

    if not has_error_body:
        assert_has_fields_in_response_content(
            fields=tree_listing,
            response_content=content[0],
        )
        assert_has_fields_in_response_content(
            fields=tree_listing_test_status,
            response_content=content[0]["test_status"],
        )
        assert_has_fields_in_response_content(
            fields=tree_listing_test_status,
            response_content=content[0]["boot_status"],
        )
        assert_has_fields_in_response_content(
            fields=tree_listing_build_status,
            response_content=content[0]["build_status"],
        )

        if pytestconfig.getoption("--run-all") and len(content) > 1:
            for tree in content[1:]:
                assert_has_fields_in_response_content(
                    fields=tree_listing,
                    response_content=tree,
                )
                assert_has_fields_in_response_content(
                    fields=tree_listing_test_status,
                    response_content=tree["test_status"],
                )
                assert_has_fields_in_response_content(
                    fields=tree_listing_test_status,
                    response_content=tree["boot_status"],
                )
                assert_has_fields_in_response_content(
                    fields=tree_listing_build_status,
                    response_content=tree["build_status"],
                )
