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
            "dashboard_kci_dev_requests_by_version_total",
        ]


@pytest.mark.parametrize(
    ("user_agent", "browser", "os", "device", "client", "kci_dev_version"),
    [
        ("kci-dev/0.1.11", "kci-dev", "unknown", "cli", Client.KCI_DEV, "0.1.11"),
        (
            "kci-dev/0.1.11 (Linux)",
            "kci-dev",
            "Linux",
            "cli",
            Client.KCI_DEV,
            "0.1.11",
        ),
        (
            "kci-dev/0.1.11 (LINUX)",
            "kci-dev",
            "Linux",
            "cli",
            Client.KCI_DEV,
            "0.1.11",
        ),
        (
            "kci-dev/0.1.11 (macos)",
            "kci-dev",
            "macOS",
            "cli",
            Client.KCI_DEV,
            "0.1.11",
        ),
        (
            "kci-dev/0.1.11 (Windows)",
            "kci-dev",
            "Windows",
            "cli",
            Client.KCI_DEV,
            "0.1.11",
        ),
        (
            "kci-dev/0.1.11 (unknown)",
            "kci-dev",
            "unknown",
            "cli",
            Client.KCI_DEV,
            "0.1.11",
        ),
        (
            "kci-dev/0.1.11.dev0 (Linux)",
            "kci-dev",
            "Linux",
            "cli",
            Client.KCI_DEV,
            "0.1.11.dev0",
        ),
        (
            "kci-dev/unknown (Linux)",
            "kci-dev",
            "Linux",
            "cli",
            Client.KCI_DEV,
            "unknown",
        ),
        (
            "kci-dev/not-a-release",
            "kci-dev",
            "unknown",
            "cli",
            Client.KCI_DEV,
            "unknown",
        ),
        ("kci-dev", "kci-dev", "unknown", "cli", Client.KCI_DEV, "unknown"),
        ("", "unknown", "unknown", "unknown", Client.UNKNOWN, None),
        ("kci-devtools/1.0", "unknown", "unknown", "desktop", Client.UNKNOWN, None),
        ("Go-http-client/1.1", "unknown", "unknown", "desktop", Client.UNKNOWN, None),
        ("curl/8.5.0", "curl", "unknown", "script", Client.SCRIPT, None),
        (
            "python-requests/2.32.3",
            "python-requests",
            "unknown",
            "script",
            Client.SCRIPT,
            None,
        ),
        (
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "bot",
            "bot",
            "bot",
            Client.BOT,
            None,
        ),
        (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Chrome",
            "Linux",
            "desktop",
            Client.DASHBOARD,
            None,
        ),
    ],
)
def test_get_client_info(user_agent, browser, os, device, client, kci_dev_version):
    info = get_client_info(user_agent)
    assert info.browser == browser
    assert info.os == os
    assert info.device == device
    assert info.client == client
    assert info.kci_dev_version == kci_dev_version
