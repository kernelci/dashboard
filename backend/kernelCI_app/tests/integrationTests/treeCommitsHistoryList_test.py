from http import HTTPStatus

import pytest

from kernelCI_app.tests.utils.asserts import assert_status_code_and_error_response
from kernelCI_app.tests.utils.client.treeClient import TreeClient
from kernelCI_app.utils import string_to_json
from requests import Response

client = TreeClient()


def request_data(query: dict) -> tuple[Response, dict]:
    response = client.get_tree_commits_history_list(query=query)
    content = string_to_json(response.content.decode())
    return response, content


@pytest.mark.parametrize(
    "query, status_code, has_error_body",
    [
        (
            {"origin": "maestro", "commit_hashes": "invalid_hash"},
            HTTPStatus.OK,
            True,
        ),
        (
            {"origin": "maestro"},
            HTTPStatus.BAD_REQUEST,
            True,
        ),
        (
            {
                "origin": "maestro",
                "git_url": "https://android.googlesource.com/kernel/common",
                "git_branch": "android-mainline",
                "commit_hashes": ",".join(
                    [
                        "ef143cc9d68aecf16ec4942e399e7699266b288f",
                        "fdf4d20b86285d7b4d1c2d3349a1bd1bc41b24ba",
                    ]
                ),
            },
            HTTPStatus.OK,
            False,
        ),
    ],
)
def test_tree_commits_history_list(
    query: dict, status_code: HTTPStatus, has_error_body: bool
) -> None:
    response, content = request_data(query)
    actual_status = response.status_code
    if isinstance(status_code, list):
        assert actual_status in status_code, (
            f"Expected one of {status_code}, got {actual_status}"
        )
    else:
        assert_status_code_and_error_response(
            response=response,
            content=content,
            status_code=status_code,
            should_error=has_error_body,
        )

    if not has_error_body and actual_status == HTTPStatus.OK:
        for commit_data in content:
            assert "git_commit_hash" in commit_data
            assert "builds" in commit_data
            assert "boots" in commit_data
            assert "tests" in commit_data


@pytest.mark.parametrize(
    "query",
    [
        (
            {
                "origin": "maestro",
                "commit_hashes": ",".join(
                    [
                        "ef143cc9d68aecf16ec4942e399e7699266b288f",
                        "fdf4d20b86285d7b4d1c2d3349a1bd1bc41b24ba",
                    ]
                ),
                "types": "builds",
            }
        ),
        (
            {
                "origin": "maestro",
                "commit_hashes": ",".join(
                    [
                        "ef143cc9d68aecf16ec4942e399e7699266b288f",
                        "fdf4d20b86285d7b4d1c2d3349a1bd1bc41b24ba",
                    ]
                ),
                "types": "tests",
            }
        ),
    ],
)
def test_tree_commits_history_list_with_types(query: dict) -> None:
    response, content = request_data(query)
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=HTTPStatus.OK,
        should_error=False,
    )
