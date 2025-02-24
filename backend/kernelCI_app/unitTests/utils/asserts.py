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
