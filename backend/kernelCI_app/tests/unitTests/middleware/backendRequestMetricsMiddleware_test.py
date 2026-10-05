from unittest.mock import MagicMock

import pytest
from django.http import HttpResponse
from django.test import RequestFactory

from kernelCI_app.middleware.backendRequestMetricsMiddleware import (
    BackendRequestMetricsMiddleware,
    Client,
    get_client_info,
)

MIDDLEWARE_MODULE = "kernelCI_app.middleware.backendRequestMetricsMiddleware"


def _middleware():
    return BackendRequestMetricsMiddleware(lambda request: HttpResponse())


def _patch_counters(monkeypatch) -> list[str]:
    created: list[str] = []
    monkeypatch.setattr(
        f"{MIDDLEWARE_MODULE}.Counter",
        lambda *args, **kwargs: created.append(args[0]) or MagicMock(),
    )
    monkeypatch.setattr(f"{MIDDLEWARE_MODULE}._metrics", None)
    return created


class TestMiddlewareCall:
    def test_constructing_middleware_does_not_create_counters(self, monkeypatch):
        created = _patch_counters(monkeypatch)
        _middleware()
        assert created == []

    def test_non_api_request_does_not_create_counters(self, monkeypatch):
        created = _patch_counters(monkeypatch)
        _middleware()(RequestFactory().get("/health/"))
        assert created == []

    def test_api_request_creates_counters(self, monkeypatch):
        created = _patch_counters(monkeypatch)
        monkeypatch.setattr(
            f"{MIDDLEWARE_MODULE}.cache.add", lambda *args, **kwargs: False
        )
        _middleware()(
            RequestFactory().get(
                "/api/tree/",
                HTTP_USER_AGENT="Mozilla/5.0",
                REMOTE_ADDR="192.0.2.1",
            )
        )
        assert created == [
            "dashboard_backend_requests_by_client_total",
            "dashboard_unique_visitors_total",
            "dashboard_unique_visitors_by_endpoint_total",
        ]


@pytest.mark.parametrize(
    ("user_agent", "browser", "os", "device", "client"),
    [
        ("kci-dev/0.1.11", "kci-dev/0.1.11", "unknown", "cli", Client.KCI_DEV),
        ("kci-dev/0.1.11 (Linux)", "kci-dev/0.1.11", "Linux", "cli", Client.KCI_DEV),
        ("kci-dev/0.1.11 (LINUX)", "kci-dev/0.1.11", "Linux", "cli", Client.KCI_DEV),
        ("kci-dev/0.1.11 (macos)", "kci-dev/0.1.11", "macOS", "cli", Client.KCI_DEV),
        (
            "kci-dev/0.1.11 (Windows)",
            "kci-dev/0.1.11",
            "Windows",
            "cli",
            Client.KCI_DEV,
        ),
        (
            "kci-dev/0.1.11 (unknown)",
            "kci-dev/0.1.11",
            "unknown",
            "cli",
            Client.KCI_DEV,
        ),
        ("kci-dev", "kci-dev", "unknown", "cli", Client.KCI_DEV),
        ("", "unknown", "unknown", "unknown", Client.UNKNOWN),
        ("kci-devtools/1.0", "unknown", "unknown", "desktop", Client.UNKNOWN),
        ("Go-http-client/1.1", "unknown", "unknown", "desktop", Client.UNKNOWN),
        ("curl/8.5.0", "curl", "unknown", "script", Client.SCRIPT),
        (
            "python-requests/2.32.3",
            "python-requests",
            "unknown",
            "script",
            Client.SCRIPT,
        ),
        (
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "bot",
            "bot",
            "bot",
            Client.BOT,
        ),
        (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Chrome",
            "Linux",
            "desktop",
            Client.DASHBOARD,
        ),
    ],
)
def test_get_client_info(user_agent, browser, os, device, client):
    info = get_client_info(user_agent)
    assert info.browser == browser
    assert info.os == os
    assert info.device == device
    assert info.client == client
