from http import HTTPStatus

from kernelCI_app.tests.utils.asserts import (
    assert_has_fields_in_response_content,
    assert_status_code_and_error_response,
)
from kernelCI_app.tests.utils.client.labOriginsClient import LabOriginsClient
from kernelCI_app.tests.utils.fields.origins import lab_origins_expected_fields
from kernelCI_app.utils import string_to_json

client = LabOriginsClient()


def test_get_lab_origins():
    response = client.get_lab_origins()
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=HTTPStatus.OK,
        should_error=False,
    )

    assert_has_fields_in_response_content(
        fields=lab_origins_expected_fields, response_content=content
    )
