from kernelCI_app.unitTests.utils.healthCheck import online
from kernelCI_app.unitTests.utils.client.hardwareClient import HardwareClient
from kernelCI_app.unitTests.utils.asserts import assert_status_code_and_error_response
from kernelCI_app.utils import string_to_json
from http import HTTPStatus
from kernelCI_app.typeModels.hardwareDetails import HardwareDetailsPostBody
import copy


client = HardwareClient()

UNEXISTENT_HARDWARE_ID = {
    "id": "no hardware id",
    "body": HardwareDetailsPostBody(
        origin="",
        startTimestampInSeconds=1737487800,
        endTimestampInSeconds=1737574200,
        selectedCommits={},
        filter={},
    ),
}

BAD_REQUEST_REQUEST_BODY = {
    "id": "google,juniper",
    "body": HardwareDetailsPostBody(
        origin="",
        startTimestampInSeconds="",
        endTimestampInSeconds="",
        selectedCommits={},
        filter={},
    ),
}

GOOGLE_JUNIPER_HARDWARE_WITHOUT_FILTERS = {
    "id": "google,juniper",
    "body": HardwareDetailsPostBody(
        startTimestampInSeconds=1740227400,
        endTimestampInSeconds=1740659400,
        selectedCommits={},
        filter={},
    ),
}

ARM_JUNO_HARDWARE_WITHOUT_FILTERS = {
    "id": "arm,juno",
    "body": HardwareDetailsPostBody(
        startTimestampInSeconds=1740232800,
        endTimestampInSeconds=1740664800,
        selectedCommits={},
        filter={},
    ),
}

GOOGLE_JUNIPER_HARDWARE_WITH_FILTERS = copy.deepcopy(
    GOOGLE_JUNIPER_HARDWARE_WITHOUT_FILTERS
)
GOOGLE_JUNIPER_HARDWARE_WITH_FILTERS["body"].filter = {
    "filter_architecture": ["arm64"],
    "filter_boot.status": ["PASS"],
}

HARDWARE_WITH_UNEXISTENT_FILTER_VALUE = copy.deepcopy(
    GOOGLE_JUNIPER_HARDWARE_WITHOUT_FILTERS
)
HARDWARE_WITH_UNEXISTENT_FILTER_VALUE["body"].filter = {
    "filter_architecture": ["invalid"]
}

HARDWARE_WITH_GLOBAL_FILTER = {
    "id": "aaeon-UPN-EHLX4RE-A10-0864",
    "body": HardwareDetailsPostBody(
        startTimestampInSeconds=1740241800,
        endTimestampInSeconds=1740673800,
        selectedCommits={},
        filter={
            "filter_architecture": ["i386"],
            "filter_config_name": ["defconfig"],
            "filter_compiler": ["gcc-12"],
            "filter_valid": ["true"],
        },
    ),
}

HARDWARE_WITH_LOCAL_FILTER = {
    "id": "google,kevin-rev15",
    "body": HardwareDetailsPostBody(
        startTimestampInSeconds=1740243600,
        endTimestampInSeconds=1740675600,
        selectedCommits={},
        filter={
            "filter_boot.issue": ["maestro:e602fca280d85d8e603f7c0aff68363bb0cd7993"],
            "filter_boot.status": ["PASS", "MISS"],
            "filter_test.status": ["DONE", "FAIL"],
            "filter_test.platform": ["rk3399-gru-kevin"],
        },
    ),
}

SUCCESS_EXPECTED_RESPONSE = {
    "expected_status": HTTPStatus.OK,
    "has_error": False,
    "check_emptiness": False,
}

ERROR_EXPECTED_RESPONSE = {
    "expected_status": HTTPStatus.OK,
    "has_error": True,
    "check_emptiness": False,
}

BAD_REQUEST_EXPECTED_RESPONSE = {
    "expected_status": HTTPStatus.BAD_REQUEST,
    "has_error": True,
    "check_emptiness": False,
}

EMPTY_EXPECTED_RESPONSE = {
    "expected_status": HTTPStatus.OK,
    "has_error": False,
    "check_emptiness": True,
}


def pytest_generate_tests(metafunc):
    base_cases = [
        ((BAD_REQUEST_REQUEST_BODY), BAD_REQUEST_EXPECTED_RESPONSE),
        ((GOOGLE_JUNIPER_HARDWARE_WITHOUT_FILTERS), SUCCESS_EXPECTED_RESPONSE),
        ((HARDWARE_WITH_UNEXISTENT_FILTER_VALUE), EMPTY_EXPECTED_RESPONSE),
    ]
    extra_cases = []
    builds_and_boots_cases = [
        ((GOOGLE_JUNIPER_HARDWARE_WITH_FILTERS), SUCCESS_EXPECTED_RESPONSE)
    ]

    if metafunc.config.getoption("--run-all"):
        extra_cases = [
            ((ARM_JUNO_HARDWARE_WITHOUT_FILTERS), SUCCESS_EXPECTED_RESPONSE),
            ((UNEXISTENT_HARDWARE_ID), ERROR_EXPECTED_RESPONSE),
            ((HARDWARE_WITH_GLOBAL_FILTER), SUCCESS_EXPECTED_RESPONSE),
        ]

    if "test_hardware_boots" in metafunc.fixturenames:
        metafunc.parametrize(
            "test_hardware_boots,expected_response",
            base_cases + extra_cases + builds_and_boots_cases,
        )

    if "test_hardware_builds" in metafunc.fixturenames:
        metafunc.parametrize(
            "test_hardware_builds,expected_response",
            base_cases + extra_cases + builds_and_boots_cases,
        )

    if "test_hardware_tests" in metafunc.fixturenames:
        metafunc.parametrize(
            "test_hardware_tests,expected_response", base_cases + extra_cases
        )


@online
def test_get_hardware_details_boots(test_hardware_boots: dict, expected_response: dict):
    expected_status, has_error, check_emptiness = expected_response.values()
    hardware_id = test_hardware_boots["id"]
    body = test_hardware_boots["body"]
    response = client.get_hardware_boots(hardware_id=hardware_id, body=body)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=expected_status,
        should_error=has_error,
    )

    if check_emptiness:
        assert len(content["boots"]) == 0


@online
def test_get_hardware_details_builds(
    test_hardware_builds: dict, expected_response: dict
):
    expected_status, has_error, check_emptiness = expected_response.values()
    hardware_id = test_hardware_builds["id"]
    body = test_hardware_builds["body"]
    response = client.get_hardware_builds(hardware_id=hardware_id, body=body)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=expected_status,
        should_error=has_error,
    )

    if check_emptiness:
        assert len(content["builds"]) == 0


@online
def test_get_hardware_details_tests(test_hardware_tests: dict, expected_response: dict):
    expected_status, has_error, check_emptiness = expected_response.values()
    hardware_id = test_hardware_tests["id"]
    body = test_hardware_tests["body"]
    response = client.get_hardware_tests(hardware_id=hardware_id, body=body)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=expected_status,
        should_error=has_error,
    )

    if check_emptiness:
        assert len(content["tests"]) == 0
