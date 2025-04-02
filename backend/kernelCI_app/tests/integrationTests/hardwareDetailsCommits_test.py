import pytest
from kernelCI_app.typeModels.hardwareDetails import (
    CommitHistoryPostBody,
    CommitHead,
)
from kernelCI_app.tests.utils.client.hardwareClient import HardwareClient
from kernelCI_app.utils import string_to_json
from kernelCI_app.tests.utils.asserts import (
    assert_status_code_and_error_response,
    assert_has_fields_in_response_content,
)
from kernelCI_app.tests.utils.fields.hardware import hardware_history_checkouts
from http import HTTPStatus
import copy

client = HardwareClient()

INVALID_REQUEST_BODY = {
    "id": "invalid",
    "body": CommitHistoryPostBody(
        origin="",
        startTimestampInSeconds="",
        endTimestampInSeconds="",
        commitHeads=[],
    ),
}

HARDWARE_NOT_FOUND = {
    "id": "no hardware id",
    "body": CommitHistoryPostBody(
        origin="maestro",
        startTimestampInSeconds=1737487800,
        endTimestampInSeconds=1737574200,
        commitHeads=[],
    ),
}

HARDWARE_WITHOUT_COMMIT_HEADS = copy.deepcopy(HARDWARE_NOT_FOUND)
HARDWARE_WITHOUT_COMMIT_HEADS["id"] = "fsl,imx6q-sabrelite"

SABRELITE_HARDWARE = copy.deepcopy(HARDWARE_WITHOUT_COMMIT_HEADS)
SABRELITE_HARDWARE["body"].commitHeads = [
    CommitHead(
        treeName="android",
        repositoryUrl="https://android.googlesource.com/kernel/common",
        branch="android11-5.4",
        commitHash="7e39477098b50156535c8f910fee50d6dac2a793",
    ),
    CommitHead(
        treeName="android",
        repositoryUrl="https://android.googlesource.com/kernel/common",
        branch="android12-5.10",
        commitHash="4fd7634f32ffbb4fd4c09b757aa16327626a1749",
    ),
    CommitHead(
        treeName="android",
        repositoryUrl="https://android.googlesource.com/kernel/common",
        branch="android12-5.10-lts",
        commitHash="f72ba1ba267f4c42adb82037e8614d7844badeb9",
    ),
]


@pytest.mark.parametrize(
    "base_hardware, status_code, has_error_body",
    [
        (HARDWARE_NOT_FOUND, HTTPStatus.OK, True),
        (INVALID_REQUEST_BODY, HTTPStatus.BAD_REQUEST, True),
        (HARDWARE_WITHOUT_COMMIT_HEADS, HTTPStatus.OK, True),
        (SABRELITE_HARDWARE, HTTPStatus.OK, False),
    ],
)
def test_get_hardware_details_commit_history(
    pytestconfig, base_hardware: dict, status_code: int, has_error_body: bool
):
    id, body = base_hardware.values()
    response = client.post_hardware_details_commit_history(hardware_id=id, body=body)
    content = string_to_json(response.content.decode())

    assert_status_code_and_error_response(
        response=response,
        status_code=status_code,
        should_error=has_error_body,
        content=content,
    )

    if not has_error_body:
        assert "commit_history_table" in content

        for _, commit_data in content["commit_history_table"].items():
            assert_has_fields_in_response_content(
                fields=hardware_history_checkouts, response_content=commit_data[0]
            )

            if pytestconfig.getoption("--run-all") and len(commit_data) > 1:
                for commit in commit_data[1:]:
                    assert_has_fields_in_response_content(
                        fields=hardware_history_checkouts, response_content=commit
                    )
