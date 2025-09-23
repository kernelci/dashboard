from kernelCI_app.typeModels.testDetails import TestStatusSeriesRequest
from kernelCI_app.tests.utils.client.testClient import TestClient
from kernelCI_app.tests.utils.asserts import (
    assert_status_code_and_error_response,
    assert_has_fields_in_response_content,
)
from kernelCI_app.tests.utils.fields.tests import (
    test_series_response_expected_fields,
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
            # maestro:68c3e1c661dc41d269171fe1
            TestStatusSeriesRequest(
                path="ltp",
                platform="imx6q-sabrelite",
                config_name="multi_v7_defconfig",
                architecture="arm",
                compiler="gcc-12",
            ),
            HTTPStatus.OK,
            False,
        ),
        (
            TestStatusSeriesRequest(
                path="non-existent-path",
            ),
            HTTPStatus.OK,
            True,
        ),
        (
            # maestro:68ba7c39b9811ea53d062635
            TestStatusSeriesRequest(
                path="kunit.exec.time_test_cases.time64_to_tm_test_date_range",
                platform="kubernetes",
                architecture="x86_64",
            ),
            HTTPStatus.OK,
            False,
        ),
    ],
)
def test_get_test_series(
    pytestconfig,
    params: TestStatusSeriesRequest,
    status_code,
    has_error_body,
):
    response = client.get_test_series(query=params)
    content = string_to_json(response.content.decode())
    if "warning" in content:
        pytest.skip("Skipping test because the migrations have not been run yet")

    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=status_code,
        should_error=has_error_body,
    )

    if not has_error_body:
        assert_has_fields_in_response_content(
            fields=test_series_response_expected_fields, response_content=content
        )

        # Verify status_history contains expected fields
        status_history = content.get("status_history", [])
        assert len(status_history) > 0, "status_history should not be empty"

        for status_history_item in status_history:
            assert_has_fields_in_response_content(
                fields=status_history_item_fields, response_content=status_history_item
            )
            if not pytestconfig.getoption("--run-all"):
                break

        test_series = content.get("test_series")
        build_series = content.get("build_series")
        assert (
            isinstance(test_series, str) and len(test_series) == 32
        ), f"test_series should be a 32-character MD5 hash, got: {test_series}"
        assert (
            isinstance(build_series, str) and len(build_series) == 32
        ), f"build_series should be a 32-character MD5 hash, got: {build_series}"


def test_get_test_series_platform_quoting():
    """Test that platform parameter handles quoting correctly"""
    params_unquoted = TestStatusSeriesRequest(
        path="fluster.debian.v4l2.gstreamer_av1.validate-fluster-results",
        platform="mt8195-cherry-tomato-r2",
        group_size=5,
    )

    params_quoted = TestStatusSeriesRequest(
        path="fluster.debian.v4l2.gstreamer_av1.validate-fluster-results",
        platform='"mt8195-cherry-tomato-r2"',
        group_size=5,
    )

    response_unquoted = client.get_test_series(query=params_unquoted)
    response_quoted = client.get_test_series(query=params_quoted)

    content_unquoted = string_to_json(response_unquoted.content.decode())
    content_quoted = string_to_json(response_quoted.content.decode())

    # Both should return the same test_series hash since the platform
    # should be normalized to the quoted version

    if "warning" in content_unquoted or "warning" in content_quoted:
        pytest.skip("Skipping test because the migrations have not been run yet")

    assert_has_fields_in_response_content(
        fields=test_series_response_expected_fields, response_content=content_unquoted
    )
    assert_has_fields_in_response_content(
        fields=test_series_response_expected_fields, response_content=content_unquoted
    )

    assert (
        content_unquoted["test_series"] == content_quoted["test_series"]
    ), "Quoted and unquoted platforms should result in the same test_series hash"
