import re
from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.middleware.backendRequestMetricsMiddleware import get_metrics

# Keys of FileRoutesByTo in dashboard/src/routeTree.gen.ts.
# A test fails when the two lists diverge.
DASHBOARD_ROUTES = frozenset(
    {
        "/",
        "/$",
        "/b/$buildId",
        "/build/$buildId",
        "/c/$treeName/$branch",
        "/c/$treeName/$branch/$hash",
        "/checkout/$treeName/$branch",
        "/checkout/$treeName/$branch/$hash",
        "/hardware",
        "/hardware/$hardwareId",
        "/hardware/$hardwareId/boot",
        "/hardware/$hardwareId/boot/$bootId",
        "/hardware/$hardwareId/build",
        "/hardware/$hardwareId/build/$buildId",
        "/hardware/$hardwareId/test",
        "/hardware/$hardwareId/test/$testId",
        "/i",
        "/i/$issueId",
        "/issue/$issueId",
        "/issues",
        "/labs",
        "/log-viewer",
        "/metrics",
        "/privacy",
        "/t/$testId",
        "/test/$testId",
        "/tree",
        "/tree/$treeId",
        "/tree/$treeId/build/$buildId",
        "/tree/$treeId/test/$testId",
        "/tree/$treeName/$branch",
        "/tree/$treeName/$branch/$hash",
        "/tree/$treeName/$branch/compare",
    }
)

MAX_VISIBLE_MS = 86_400_000
MAX_PATH_LENGTH = 2_000


def _path_matcher(pattern: str) -> re.Pattern[str] | None:
    segments = pattern.strip("/").split("/")
    # /$ is the not-found splat. It would accept every path.
    if any(segment == "$" for segment in segments):
        return None
    parts = [
        "[^/]+" if segment.startswith("$") else re.escape(segment)
        for segment in segments
    ]
    return re.compile("^/" + "/".join(parts) + "$")


_PATH_MATCHERS = tuple(
    matcher
    for pattern in DASHBOARD_ROUTES
    if (matcher := _path_matcher(pattern)) is not None
)


def is_dashboard_path(path: str) -> bool:
    return any(matcher.match(path) for matcher in _PATH_MATCHERS)


class VisibleTimeSerializer(serializers.Serializer):
    route = serializers.CharField(max_length=MAX_PATH_LENGTH)
    time_ms = serializers.IntegerField(min_value=0, max_value=MAX_VISIBLE_MS)


class VisibleTimeView(APIView):
    authentication_classes = []

    @extend_schema(
        request=VisibleTimeSerializer,
        responses={
            HTTPStatus.NO_CONTENT: None,
            HTTPStatus.BAD_REQUEST: None,
        },
    )
    def post(self, request) -> Response:
        body = VisibleTimeSerializer(data=request.data)
        if not body.is_valid() or not is_dashboard_path(body.validated_data["route"]):
            return Response(status=HTTPStatus.BAD_REQUEST)
        route = body.validated_data["route"]
        get_metrics().route_visible_seconds.labels(route=route).observe(
            body.validated_data["time_ms"] / 1000
        )
        return Response(status=HTTPStatus.NO_CONTENT)
