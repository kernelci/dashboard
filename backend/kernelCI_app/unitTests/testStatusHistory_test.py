from kernelCI_app.typeModels.testDetails import TestStatusHistoryRequest
from kernelCI_app.unitTests.utils.healthCheck import online
from kernelCI_app.unitTests.utils.client.testClient import TestClient
from kernelCI_app.unitTests.utils.asserts import (
    assert_status_code_and_error_response,
    assert_has_fields_in_response_content,
)
from kernelCI_app.unitTests.utils.fields.tests import status_history_expected_fields
from kernelCI_app.utils import string_to_json
import pytest
from http import HTTPStatus


client = TestClient()


@online
@pytest.mark.parametrize(
    "params, status_code, has_error_body",
    [
        (
            TestStatusHistoryRequest(
                path="fluster.debian.v4l2.gstreamer_av1.validate-fluster-results",
                origin="maestro",
                git_repository_url="https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                git_repository_branch="master",
                platform="mt8195-cherry-tomato-r2",
                current_test_timestamp="2025-03-10T01:52:01.230777Z",
            ),
            HTTPStatus.OK,
            False,
        ),
        (
            TestStatusHistoryRequest(
                path="unexistent",
                origin="maestro",
                current_test_timestamp="2025-03-10T01:39:01.486560Z",
            ),
            HTTPStatus.BAD_REQUEST,
            True,
        ),
    ],
)
def test_get(params: TestStatusHistoryRequest, status_code, has_error_body):
    response = client.get_test_status_history(query=params)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=status_code,
        should_error=has_error_body,
    )

    if not has_error_body:
        assert_has_fields_in_response_content(
            fields=status_history_expected_fields, response_content=content
        )
