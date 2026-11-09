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
# treeId is a commit hash, so it is not kept.
_KEEP_PARAMS = frozenset({"hardwareId", "treeName", "branch"})


def _segments(value: str) -> list[str]:
    return [segment for segment in value.split("/") if segment]


def _apply_pattern(pattern: str, path: str) -> str | None:
    # /$ is the not-found splat. It would accept every path.
    if pattern == "/$":
        return None
    pattern_segments = _segments(pattern)
    path_segments = _segments(path)
    if len(pattern_segments) != len(path_segments):
        return None
    label_segments = []
    for pattern_segment, path_segment in zip(
        pattern_segments, path_segments, strict=True
    ):
        if pattern_segment.startswith("$"):
            label_segments.append(
                path_segment if pattern_segment[1:] in _KEEP_PARAMS else pattern_segment
            )
        elif pattern_segment != path_segment:
            return None
        else:
            label_segments.append(pattern_segment)
    if not label_segments:
        return "/"
    return "/" + "/".join(label_segments)


def route_label(path: str) -> str | None:
    matches = [
        (pattern, label)
        for pattern in DASHBOARD_ROUTES
        if (label := _apply_pattern(pattern, path)) is not None
    ]
    if not matches:
        return None
    # More fixed segments wins. Fewer placeholders breaks a tie, so a branch
    # named "build" stays on the compare route.
    return max(
        matches,
        key=lambda item: (
            sum(not segment.startswith("$") for segment in _segments(item[0])),
            -item[1].count("$"),
        ),
    )[1]


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
        label = route_label(body.validated_data["route"]) if body.is_valid() else None
        if label is None:
            return Response(status=HTTPStatus.BAD_REQUEST)
        get_metrics().route_visible_seconds.labels(route=label).observe(
            body.validated_data["time_ms"] / 1000
        )
        return Response(status=HTTPStatus.NO_CONTENT)
