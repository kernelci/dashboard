from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from django.http import HttpResponse
from django.test import RequestFactory

from kernelCI_app.middleware.backendRequestMetricsMiddleware import (
    BackendRequestMetricsMiddleware,
    Client,
    Metrics,
    PrometheusAfterMiddleware,
    get_client_info,
)

MIDDLEWARE_MODULE = "kernelCI_app.middleware.backendRequestMetricsMiddleware"


def _middleware():
    return BackendRequestMetricsMiddleware(lambda request: HttpResponse())


def _patch_counters(monkeypatch) -> list[str]:
    created: list[str] = []

    def fake_metric(*args, **kwargs):
        created.append(args[0])
        return MagicMock()

    monkeypatch.setattr(f"{MIDDLEWARE_MODULE}.Counter", fake_metric)
    monkeypatch.setattr(f"{MIDDLEWARE_MODULE}.Histogram", fake_metric)
    monkeypatch.setattr(f"{MIDDLEWARE_MODULE}._metrics", None)
    return created


def _fake_metrics(monkeypatch) -> tuple[MagicMock, MagicMock]:
    counter = MagicMock()
    histogram = MagicMock()
    monkeypatch.setattr(
        f"{MIDDLEWARE_MODULE}._metrics",
        Metrics(
            requests_by_client=counter,
            unique_visitors=MagicMock(),
            unique_visitors_by_endpoint=MagicMock(),
            request_latency=histogram,
        ),
    )
    monkeypatch.setattr(f"{MIDDLEWARE_MODULE}.cache.add", lambda *args, **kwargs: False)
    return counter, histogram


def _api_request(user_agent: str):
    request = RequestFactory().get("/api/schema/", HTTP_USER_AGENT=user_agent)
    request.resolver_match = SimpleNamespace(url_name="schema", view_name="schema")
    return request


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
            "dashboard_backend_request_latency_seconds",
        ]


def test_api_request_records_client_on_counter_and_histogram(monkeypatch):
    counter, histogram = _fake_metrics(monkeypatch)
    django_latency = MagicMock()
    after = PrometheusAfterMiddleware(lambda request: HttpResponse())
    monkeypatch.setattr(
        after.metrics, "requests_latency_by_view_method", django_latency
    )
    BackendRequestMetricsMiddleware(after)(_api_request("kci-dev/0.1.11"))

    assert counter.labels.call_args.kwargs["endpoint"] == "schema"
    assert counter.labels.call_args.kwargs["client"] == Client.KCI_DEV
    assert histogram.labels.call_args.kwargs == {
        "endpoint": "schema",
        "client": Client.KCI_DEV,
    }
    histogram.labels.return_value.observe.assert_called_once()
    django_latency.labels.assert_not_called()


def test_admin_request_stays_on_django_latency_histogram(monkeypatch):
    counter, histogram = _fake_metrics(monkeypatch)
    django_latency = MagicMock()
    after = PrometheusAfterMiddleware(lambda request: HttpResponse())
    monkeypatch.setattr(
        after.metrics, "requests_latency_by_view_method", django_latency
    )
    BackendRequestMetricsMiddleware(after)(RequestFactory().get("/admin/"))

    django_latency.labels.assert_called_once()
    django_latency.labels.return_value.observe.assert_called_once()
    counter.labels.assert_not_called()
    histogram.labels.assert_not_called()


@pytest.mark.parametrize(
    ("user_agent", "browser", "os", "device", "client"),
    [
        ("kci-dev/0.1.11", "kci-dev/0.1.11", "unknown", "cli", Client.KCI_DEV),
        ("kci-dev/0.1.11 (Linux)", "kci-dev/0.1.11", "Linux", "cli", Client.KCI_DEV),
        ("kci-dev/0.1.11 (macos)", "kci-dev/0.1.11", "macOS", "cli", Client.KCI_DEV),
        ("kci-dev", "kci-dev", "unknown", "cli", Client.KCI_DEV),
        ("kci-devtools/1.0", "unknown", "unknown", "desktop", Client.DASHBOARD),
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
