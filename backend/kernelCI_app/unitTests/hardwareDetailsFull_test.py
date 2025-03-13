from kernelCI_app.unitTests.utils.healthCheck import online
from kernelCI_app.unitTests.utils.client.hardwareClient import HardwareClient
from kernelCI_app.unitTests.utils.asserts import (
    assert_status_code_and_error_response,
    assert_has_fields_in_response_content,
)
from kernelCI_app.unitTests.utils.fields import hardware
from kernelCI_app.utils import string_to_json
from kernelCI_app.unitTests.utils.hardwareDetailsCommonTestCases import (
    ALLWINNER_HARDWARE,
    UNEXISTENT_HARDWARE_ID,
    BAD_REQUEST_REQUEST_BODY,
    GOOGLE_JUNIPER_HARDWARE_WITHOUT_FILTERS,
    HARDWARE_WITH_UNEXISTENT_FILTER_VALUE,
    GOOGLE_JUNIPER_HARDWARE_WITH_FILTERS,
    ARM_JUNO_HARDWARE_WITHOUT_FILTERS,
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

    if metafunc.config.getoption("--run-all"):
        extra_cases = [
            ((ALLWINNER_HARDWARE), SUCCESS_EXPECTED_RESPONSE),
            ((ARM_JUNO_HARDWARE_WITHOUT_FILTERS), SUCCESS_EXPECTED_RESPONSE),
            ((UNEXISTENT_HARDWARE_ID), ERROR_EXPECTED_RESPONSE),
            ((HARDWARE_WITH_GLOBAL_FILTER), SUCCESS_EXPECTED_RESPONSE),
            ((GOOGLE_JUNIPER_HARDWARE_WITH_FILTERS), SUCCESS_EXPECTED_RESPONSE),
        ]

    if "test_hardware_details" in metafunc.fixturenames:
        metafunc.parametrize(
            "test_hardware_details,expected_response",
            base_cases + extra_cases,
        )


@online
def test_hardware_details_full(test_hardware_details, expected_response):
    expected_status, has_error, check_emptiness = expected_response.values()
    hardware_id = test_hardware_details["id"]
    body = test_hardware_details["body"]
    response = client.post_hardware_details_full(hardware_id=hardware_id, body=body)
    content = string_to_json(response.content.decode())

    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=expected_status,
        should_error=has_error,
    )

    if check_emptiness:
        assert len(content["builds"]) == 0
        assert len(content["boots"]) == 0
        assert len(content["tests"]) == 0

    if not has_error:
        assert_has_fields_in_response_content(
            fields=hardware.hardware_summary, response_content=content
        )
        assert_has_fields_in_response_content(
            fields=hardware.hardware_summary_summary,
            response_content=content["summary"],
        )
        assert_has_fields_in_response_content(
            fields=hardware.hardware_summary_common, response_content=content["common"]
        )
        assert_has_fields_in_response_content(
            fields=hardware.hardware_summary_filters,
            response_content=content["filters"],
        )
        assert_has_fields_in_response_content(
            fields=hardware.hardware_test_summary,
            response_content=content["summary"]["tests"],
        )
        assert_has_fields_in_response_content(
            fields=hardware.hardware_test_summary,
            response_content=content["summary"]["boots"],
        )
        assert_has_fields_in_response_content(
            fields=hardware.hardware_build_summary,
            response_content=content["summary"]["builds"],
        )
