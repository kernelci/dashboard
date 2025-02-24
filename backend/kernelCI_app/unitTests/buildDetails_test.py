from kernelCI_app.unitTests.utils.healthCheck import online
from kernelCI_app.unitTests.utils.buildClient import BuildClient
from kernelCI_app.unitTests.utils.asserts import (
    assert_status_code_and_error_response,
)
from kernelCI_app.utils import string_to_json
import pytest
from http import HTTPStatus


@online
@pytest.mark.parametrize(
    "build_id, status_code, has_error_body",
    [
        ("maestro:67b62592f7707533c0ff7a95", HTTPStatus.OK, False),
        ("invalid_id", HTTPStatus.OK, True),
    ],
)
def test_get(build_id, status_code, has_error_body):
    client = BuildClient()
    response = client.get_build_details(build_id=build_id)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        content=content,
        response=response,
        status_code=status_code,
        should_error=has_error_body,
    )
