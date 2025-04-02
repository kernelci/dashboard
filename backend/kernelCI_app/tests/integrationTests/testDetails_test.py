from kernelCI_app.tests.utils.client.testClient import TestClient
from kernelCI_app.tests.utils.asserts import (
    assert_status_code_and_error_response,
    assert_has_fields_in_response_content,
)
from kernelCI_app.tests.utils.fields.tests import test_expected_fields
from kernelCI_app.tests.utils.fields.issues import issues_resource_fields
from kernelCI_app.utils import string_to_json
import pytest
from http import HTTPStatus


client = TestClient()


@pytest.mark.parametrize(
    "test_id, status_code, has_error_body",
    [
        ("maestro:67b898cdf7707533c0067a02", HTTPStatus.OK, False),
        ("invalid_id", HTTPStatus.OK, True),
    ],
)
def test_get(test_id, status_code, has_error_body):
    response = client.get_test_details(test_id=test_id)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=status_code,
        should_error=has_error_body,
    )

    if not has_error_body:
        assert_has_fields_in_response_content(
            fields=test_expected_fields, response_content=content
        )


@pytest.mark.parametrize(
    "test_id, status_code, has_error_body",
    [
        ("maestro:67b898cdf7707533c0067a02", HTTPStatus.OK, True),
        ("maestro:67bd70e6323b35c54a8824a0", HTTPStatus.OK, False),
    ],
)
def test_get_issues(test_id, status_code, has_error_body):
    response = client.get_test_issues(test_id=test_id)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=status_code,
        should_error=has_error_body,
    )

    if not has_error_body:
        assert_has_fields_in_response_content(
            fields=issues_resource_fields, response_content=content[0]
        )
