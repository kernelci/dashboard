from kernelCI_app.typeModels.testDetails import TestStatusHistoryRequest
from kernelCI_app.tests.utils.client.testClient import TestClient
from kernelCI_app.tests.utils.asserts import (
    assert_status_code_and_error_response,
    assert_has_fields_in_response_content,
)
from kernelCI_app.tests.utils.fields.tests import (
    status_history_response_expected_fields,
    status_history_item_fields,
)
from kernelCI_app.utils import string_to_json
import pytest
from http import HTTPStatus


client = TestClient()


@pytest.mark.parametrize(
    "params, status_code, has_error_body",
    [
        (
            # https://staging.dashboard.kernelci.org:9000/test/maestro%3A67ce452318018371957dbf70
            TestStatusHistoryRequest(
                path="fluster.debian.v4l2.gstreamer_av1.validate-fluster-results",
                origin="maestro",
                git_repository_url="https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                git_repository_branch="master",
                platform="mt8195-cherry-tomato-r2",
                current_test_start_time="2025-03-10T01:49:23.064000Z",
                config_name="defconfig+lab-setup+arm64-chromebook"
                + "+CONFIG_MODULE_COMPRESS=n+CONFIG_MODULE_COMPRESS_NONE=y",
            ),
            HTTPStatus.OK,
            False,
        ),
        (
            TestStatusHistoryRequest(
                path="unexistent",
                origin="maestro",
                current_test_start_time="2025-03-10T01:39:01.486560Z",
                git_repository_url="unexistent",
                git_repository_branch="unexistent",
                config_name="unexistent",
            ),
            HTTPStatus.BAD_REQUEST,
            True,
        ),
    ],
)
def test_get(
    pytestconfig,
    params: TestStatusHistoryRequest,
    status_code,
    has_error_body,
):
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
            fields=status_history_response_expected_fields, response_content=content
        )

        status_history = content.get("status_history", [])

        for status_history_item in status_history:
            assert_has_fields_in_response_content(
                fields=status_history_item_fields, response_content=status_history_item
            )
            if not pytestconfig.getoption("--run-all"):
                break
