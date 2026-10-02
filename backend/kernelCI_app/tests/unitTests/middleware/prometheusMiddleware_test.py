from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import ResolverMatch
from prometheus_client import REGISTRY

from kernelCI_app.middleware.backendRequestMetricsMiddleware import (
    PrometheusAfterMiddleware as ApiLatencyAfterMiddleware,
)
from kernelCI_app.middleware.prometheusMiddleware import PrometheusAfterMiddleware

METRIC = "django_http_requests_latency_seconds_by_view_method_count"


def _count(view: str) -> float:
    return REGISTRY.get_sample_value(METRIC, {"view": view, "method": "GET"}) or 0


def _request(path: str, view: str):
    request = RequestFactory().get(path)
    request.resolver_match = ResolverMatch(lambda request: None, (), {}, url_name=view)
    return request


class TestExcludedEndpoints:
    def test_health_is_not_observed_and_other_views_are(self):
        after = PrometheusAfterMiddleware(lambda request: HttpResponse())
        response = HttpResponse()

        health = _request("/health/", "health")
        health_before = _count("health")
        after.process_request(health)
        after.process_view(health, None, (), {})
        after.process_response(health, response)
        assert _count("health") == health_before

        tree = _request("/api/tree/", "tree")
        tree_before = _count("tree")
        after.process_request(tree)
        after.process_view(tree, None, (), {})
        after.process_response(tree, response)
        assert _count("tree") == tree_before + 1


def test_api_latency_middleware_keeps_health_skip_and_splits_histograms():
    after = ApiLatencyAfterMiddleware(lambda request: HttpResponse())
    response = HttpResponse()

    health = _request("/health/", "health")
    health_before = _count("health")
    after.process_request(health)
    after.process_view(health, None, (), {})
    after.process_response(health, response)
    assert _count("health") == health_before

    tree = _request("/api/tree/", "tree")
    tree_before = _count("tree")
    after.process_request(tree)
    after.process_view(tree, None, (), {})
    after.process_response(tree, response)
    assert _count("tree") == tree_before

    admin = _request("/admin/", "admin")
    admin_before = _count("admin")
    after.process_request(admin)
    after.process_view(admin, None, (), {})
    after.process_response(admin, response)
    assert _count("admin") == admin_before + 1
