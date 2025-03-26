import pytest
from kernelCI_app.unitTests.utils.healthCheck import online
from kernelCI_app.typeModels.hardwareListing import HardwareQueryParamsDocumentationOnly
from kernelCI_app.unitTests.utils.client.hardwareClient import HardwareClient
from kernelCI_app.unitTests.utils.asserts import (
    assert_status_code_and_error_response,
    assert_has_fields_in_response_content,
)
from kernelCI_app.unitTests.utils.fields.hardware import (
    hardware_listing_fields,
    status_summary_fields,
)
from kernelCI_app.utils import string_to_json
from http import HTTPStatus


@online
@pytest.mark.parametrize(
    "query, has_error_body",
    [
        (
            HardwareQueryParamsDocumentationOnly(
                origin="maestro",
                startTimestampInSeconds="1741192200",
                endTimestampInSeconds="1741624200",
            ),
            False,
        ),
        (
            # Up until this point, redhat hasn't sent any hardwares
            HardwareQueryParamsDocumentationOnly(
                origin="redhat",
                startTimestampInSeconds="1741192200",
                endTimestampInSeconds="1741624200",
            ),
            True,
        ),
        (
            HardwareQueryParamsDocumentationOnly(
                origin="invalid_origin",
                startTimestampInSeconds="1741192200",
                endTimestampInSeconds="1741624200",
            ),
            True,
        ),
    ],
)
def test_post_hardware_listing(
    pytestconfig, query: HardwareQueryParamsDocumentationOnly, has_error_body: bool
) -> None:
    client = HardwareClient()
    response = client.get_hardware_listing(query=query)
    content = string_to_json(response.content.decode())

    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=HTTPStatus.OK,
        should_error=has_error_body,
    )

    if not has_error_body:
        hardware = content["hardware"]
        assert_has_fields_in_response_content(
            fields=hardware_listing_fields,
            response_content=hardware[0],
        )
        assert_has_fields_in_response_content(
            fields=status_summary_fields,
            response_content=hardware[0]["test_status_summary"],
        )
        assert_has_fields_in_response_content(
            fields=status_summary_fields,
            response_content=hardware[0]["boot_status_summary"],
        )
        assert_has_fields_in_response_content(
            fields=status_summary_fields,
            response_content=hardware[0]["build_status_summary"],
        )

        if pytestconfig.getoption("--run-all") and len(content["hardware"]) > 1:
            for hardware in content["hardware"][1:]:
                assert_has_fields_in_response_content(
                    fields=hardware_listing_fields,
                    response_content=hardware,
                )
                assert_has_fields_in_response_content(
                    fields=status_summary_fields,
                    response_content=hardware["test_status_summary"],
                )
                assert_has_fields_in_response_content(
                    fields=status_summary_fields,
                    response_content=hardware["boot_status_summary"],
                )
                assert_has_fields_in_response_content(
                    fields=status_summary_fields,
                    response_content=hardware["build_status_summary"],
                )
