from kernelCI_app.unitTests.utils.healthCheck import online
from kernelCI_app.unitTests.utils.client.buildClient import BuildClient
from kernelCI_app.unitTests.utils.asserts import (
    assert_status_code_and_error_response,
    assert_has_fields_in_response_content,
)
from kernelCI_app.unitTests.utils.fields.builds import (
    build_details_expected_fields,
    build_tests_expected_fields,
)
from kernelCI_app.unitTests.utils.fields.issues import issues_resource_fields
from kernelCI_app.utils import string_to_json
import pytest
from http import HTTPStatus


client = BuildClient()


@online
@pytest.mark.parametrize(
    "build_id, status_code, has_error_body",
    [
        ("maestro:67b62592f7707533c0ff7a95", HTTPStatus.OK, False),
        ("invalid_id", HTTPStatus.OK, True),
    ],
)
def test_get_build_details(
    build_id: str, status_code: HTTPStatus, has_error_body: bool
) -> None:
    response = client.get_build_details(build_id=build_id)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        content=content,
        response=response,
        status_code=status_code,
        should_error=has_error_body,
    )

    if not has_error_body:
        assert_has_fields_in_response_content(
            fields=build_details_expected_fields, response_content=content
        )


@online
@pytest.mark.parametrize(
    "build_id, status_code, has_error_body",
    [
        ("maestro:dummy_67cb759a180183719578307e_x86_64", HTTPStatus.OK, False),
        ("maestro:67ce32e418018371957d36b1", HTTPStatus.OK, False),
        ("invalid_id", HTTPStatus.OK, True),
    ],
)
def test_get_build_tests(
    pytestconfig, build_id: str, status_code: HTTPStatus, has_error_body: bool
) -> None:
    response = client.get_build_tests(build_id=build_id)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        content=content,
        response=response,
        status_code=status_code,
        should_error=has_error_body,
    )

    if not has_error_body:
        assert_has_fields_in_response_content(
            fields=build_tests_expected_fields, response_content=content[0]
        )

        if pytestconfig.getoption("--run-all") and len(content) > 1:
            for test in content[1:]:
                assert_has_fields_in_response_content(
                    fields=build_tests_expected_fields, response_content=test
                )


@online
@pytest.mark.parametrize(
    "build_id, status_code, has_error_body",
    [
        ("redhat:1701576995-x86_64-kernel", HTTPStatus.OK, False),
        ("invalid_id", HTTPStatus.OK, True),
    ],
)
def test_get_build_issues(
    pytestconfig, build_id: str, status_code: HTTPStatus, has_error_body: bool
) -> None:
    response = client.get_build_issues(build_id=build_id)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        content=content,
        response=response,
        status_code=status_code,
        should_error=has_error_body,
    )

    if not has_error_body:
        assert_has_fields_in_response_content(
            fields=issues_resource_fields, response_content=content[0]
        )

        if pytestconfig.getoption("--run-all") and len(content) > 1:
            for issue in content[1:]:
                assert_has_fields_in_response_content(
                    fields=issues_resource_fields, response_content=issue
                )
