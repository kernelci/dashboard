from kernelCI_app.tests.utils.client.hardwareClient import HardwareClient
from kernelCI_app.tests.utils.asserts import assert_status_code_and_error_response
from kernelCI_app.utils import string_to_json
from kernelCI_app.tests.utils.hardwareDetailsCommonTestCases import (
    BAD_REQUEST_REQUEST_BODY,
    GOOGLE_JUNIPER_HARDWARE_WITHOUT_FILTERS,
    HARDWARE_WITH_UNEXISTENT_FILTER_VALUE,
    GOOGLE_JUNIPER_HARDWARE_WITH_FILTERS,
    ARM_JUNO_HARDWARE_WITHOUT_FILTERS,
    UNEXISTENT_HARDWARE_ID,
    HARDWARE_WITH_GLOBAL_FILTER,
    BAD_REQUEST_EXPECTED_RESPONSE,
    SUCCESS_EXPECTED_RESPONSE,
    EMPTY_EXPECTED_RESPONSE,
    ERROR_EXPECTED_RESPONSE,
)


client = HardwareClient()


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


def test_get_hardware_details_boots(test_hardware_boots: dict, expected_response: dict):
    expected_status, has_error, check_emptiness = expected_response.values()
    hardware_id = test_hardware_boots["id"]
    body = test_hardware_boots["body"]
    response = client.post_hardware_boots(hardware_id=hardware_id, body=body)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=expected_status,
        should_error=has_error,
    )

    if check_emptiness:
        assert len(content["boots"]) == 0


def test_get_hardware_details_builds(
    test_hardware_builds: dict, expected_response: dict
):
    expected_status, has_error, check_emptiness = expected_response.values()
    hardware_id = test_hardware_builds["id"]
    body = test_hardware_builds["body"]
    response = client.post_hardware_builds(hardware_id=hardware_id, body=body)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=expected_status,
        should_error=has_error,
    )

    if check_emptiness:
        assert len(content["builds"]) == 0


def test_get_hardware_details_tests(test_hardware_tests: dict, expected_response: dict):
    expected_status, has_error, check_emptiness = expected_response.values()
    hardware_id = test_hardware_tests["id"]
    body = test_hardware_tests["body"]
    response = client.post_hardware_tests(hardware_id=hardware_id, body=body)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=expected_status,
        should_error=has_error,
    )

    if check_emptiness:
        assert len(content["tests"]) == 0
