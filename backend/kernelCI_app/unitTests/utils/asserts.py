import requests
from http import HTTPStatus


def assert_status_code(*, response: requests.Response, status_code: HTTPStatus) -> None:
    assert (
        response.status_code == status_code
    ), f"This call returned status code {response.status_code}, when it should be {status_code}."


def assert_error_response(response_content: dict) -> None:
    assert (
        "error" in response_content
    ), f"This call must return an error message. {response_content}"


def assert_status_code_and_error_response(
    *,
    response: requests.Response,
    content: dict,
    status_code: HTTPStatus,
    should_error: bool,
) -> None:
    assert_status_code(response=response, status_code=status_code)
    if should_error:
        assert_error_response(content)


def assert_has_fields_in_response_content(
    *, fields: list[str], response_content: dict
) -> None:
    for field in fields:
        assert (
            field in response_content
        ), f"Field {field} doesn't exists on {response_content}"


def assert_build_filters(*, filters: dict, build: dict):
    if filters is not None:
        for filter_key, filter_value in filters.items():
            if filter_key.startswith("boot.") or filter_key.startswith("test."):
                continue

            if filter_key.startswith("build."):
                filter_key = filter_key.split(".")[1]

            assert (
                build[filter_key] == filter_value
            ), f"Wrong value for filter field {filter_key}. {build[filter_key]} != {filter_value}"


def assert_boots_filters(*, filters: dict, boot: dict):
    if filters is not None:
        for filter_key, filter_value in filters.items():
            if not filter_key.startswith("boot.") or filter_key != "test.hardware":
                continue

            if filter_key == "test.hardware":
                field_key = "environment_compatible"
            else:
                field_key = filter_key.split(".")[1]

            assert (
                boot[field_key] == filter_value or filter_value in boot[field_key]
            ), f"Wrong value for filter field {filter_key}. {boot[filter_key]} != {filter_value}"


def assert_tests_filters(*, filters: dict, test: dict):
    if filters is not None:
        for filter_key, filter_value in filters.items():
            if not filter_key.startswith("test."):
                continue

            if filter_key == "test.hardware":
                field_key = "environment_compatible"
            else:
                field_key = filter_key.split(".")[1]

            assert (
                test[field_key] == filter_value or filter_value in test[field_key]
            ), f"Wrong value for filter field {filter_key}. {test[filter_key]} != {filter_value}"
