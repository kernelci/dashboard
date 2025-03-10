from kernelCI_app.unitTests.utils.healthCheck import online
from kernelCI_app.unitTests.utils.client.treeClient import TreeClient
from kernelCI_app.unitTests.utils.asserts import (
    assert_status_code_and_error_response,
    assert_has_fields_in_response_content,
)
from kernelCI_app.utils import string_to_json
from kernelCI_app.unitTests.utils.fields.tree import tree_fast
from http import HTTPStatus


client = TreeClient()


def pytest_generate_tests(metafunc):
    tree_listing_base_cases = [
        (
            {"origin": "maestro", "intervalInDays": "7"},
            HTTPStatus.OK,
            False,
        ),
        (
            {"origin": "invalid", "intervalInDays": "7"},
            HTTPStatus.OK,
            True,
        ),
        (
            {"origin": "maestro", "intervalInDays": "-3"},
            HTTPStatus.BAD_REQUEST,
            True,
        ),
    ]

    tree_listing_extra_cases = []
    if metafunc.config.getoption("--run-all"):
        tree_listing_extra_cases += [
            (
                {"origin": "maestro", "intervalInDays": "0"},
                HTTPStatus.BAD_REQUEST,
                True,
            ),
            (
                {"origin": "redhat", "intervalInDays": "6"},
                HTTPStatus.OK,
                False,
            ),
            (
                {"origin": "microsoft", "intervalInDays": "5"},
                HTTPStatus.OK,
                False,
            ),
            (
                {"origin": "broonie", "intervalInDays": "4"},
                HTTPStatus.OK,
                False,
            ),
            (
                {"origin": "tuxsuite", "intervalInDays": "7"},
                HTTPStatus.OK,
                False,
            ),
            (
                {"origin": "0dayci", "intervalInDays": "7"},
                HTTPStatus.OK,
                False,
            ),
            (
                {"origin": "syzbot", "intervalInDays": "7"},
                HTTPStatus.OK,
                False,
            ),
        ]

    if "tree_listing_input" in metafunc.fixturenames:
        metafunc.parametrize(
            "tree_listing_input", tree_listing_base_cases + tree_listing_extra_cases
        )


@online
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
