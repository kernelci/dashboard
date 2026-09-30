"""Skip Prometheus view metrics for a blacklist of Django URL names.

Those names are the `view` label on
`django_http_requests_latency_seconds_by_view_method`.
"""

from django_prometheus.middleware import PrometheusAfterMiddleware as _After

EXCLUDED_ENDPOINTS = frozenset({"health"})


def _excluded(request) -> bool:
    match = getattr(request, "resolver_match", None)
    return getattr(match, "view_name", None) in EXCLUDED_ENDPOINTS


class PrometheusAfterMiddleware(_After):
    def process_view(self, request, view_func, *view_args, **view_kwargs):
        if _excluded(request):
            return None
        return super().process_view(request, view_func, *view_args, **view_kwargs)

    def process_response(self, request, response):
        if _excluded(request):
            return response
        return super().process_response(request, response)

    def process_exception(self, request, exception):
        if _excluded(request):
            return None
        return super().process_exception(request, exception)
