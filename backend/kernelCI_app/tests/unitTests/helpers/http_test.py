from unittest.mock import patch

from kernelCI_app.helpers.http import CONNECT_TIMEOUT_IN_SECONDS, get, post


@patch("kernelCI_app.helpers.http.requests.get")
def test_get_pairs_connect_with_read_timeout(mock_get):
    get("https://example.com/file", timeout=30, stream=True)

    mock_get.assert_called_once_with(
        "https://example.com/file",
        timeout=(CONNECT_TIMEOUT_IN_SECONDS, 30),
        stream=True,
    )


@patch("kernelCI_app.helpers.http.requests.post")
def test_post_pairs_connect_with_read_timeout(mock_post):
    post("https://example.com/upload", timeout=10, json={"ok": True})

    mock_post.assert_called_once_with(
        "https://example.com/upload",
        timeout=(CONNECT_TIMEOUT_IN_SECONDS, 10),
        json={"ok": True},
    )
