from kernelCI_app.utils import string_to_json


def defaultTestAsserts(response, status_code, has_error_body):
    content = string_to_json(response.content.decode())
    assert (
        response.status_code == status_code
    ), f"This call give status code {response.status_code}, when it should be {status_code}."
    if has_error_body:
        assert "error" in content, "This call must return a error message."
