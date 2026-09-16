from unittest.mock import MagicMock

from django.http import HttpResponse
from django.test import RequestFactory

from kernelCI_app.middleware.backendRequestMetricsMiddleware import (
    BackendRequestMetricsMiddleware,
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
