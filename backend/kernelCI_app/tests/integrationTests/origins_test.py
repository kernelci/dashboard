from http import HTTPStatus
from kernelCI_app.tests.utils.client.originClient import OriginClient
from kernelCI_app.tests.utils.asserts import (
    assert_status_code_and_error_response,
    assert_has_fields_in_response_content,
)
from kernelCI_app.utils import string_to_json
from kernelCI_app.tests.utils.fields.origins import origins_expected_fields

client = OriginClient()


def test_get_origins():
    response = client.get_origins()
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=HTTPStatus.OK,
        should_error=False,
    )

    assert_has_fields_in_response_content(
        fields=origins_expected_fields, response_content=content
    )
