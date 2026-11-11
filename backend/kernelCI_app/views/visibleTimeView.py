import logging
import threading
from http import HTTPStatus

from django.db import DatabaseError, connection
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.middleware.backendRequestMetricsMiddleware import get_metrics

logger = logging.getLogger(__name__)

_cache_lock = threading.Lock()
_tree_cache: set[tuple[str, str]] = set()
_hardware_cache: set[str] = set()

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

MAX_VISIBLE_SECONDS = 86_400
MAX_PATH_LENGTH = 2_000


def _segments(value: str) -> list[str]:
    return [segment for segment in value.split("/") if segment]


def _tree_pair_in_checkouts(pair: tuple[str, str]) -> bool:
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM checkouts
                    WHERE tree_name = %s AND git_repository_branch = %s
                )
                """,
                pair,
            )
            return bool(cursor.fetchone()[0])
    except DatabaseError:
        logger.exception("visible time tree lookup failed")
        return False


def _hardware_id_in_status(hardware_id: str) -> bool:
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM hardware_status WHERE platform = %s
                )
                """,
                [hardware_id],
            )
            if cursor.fetchone()[0]:
                return True
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM hardware_status
                    WHERE compatibles @> ARRAY[%s]::text[]
                )
                """,
                [hardware_id],
            )
            return bool(cursor.fetchone()[0])
    except DatabaseError:
        logger.exception("visible time hardware lookup failed")
        return False


def _cached(cache: set, key, lookup) -> bool:
    if key in cache:
        return True
    if not lookup(key):
        return False
    with _cache_lock:
        cache.add(key)
    return True


def _label_segment(
    pattern_segment: str,
    values: dict[str, str],
    tree_pair_cached: bool,
    cached_hardware_id: str | None,
) -> str:
    if not pattern_segment.startswith("$"):
        return pattern_segment
    param = pattern_segment[1:]
    value = values[param]
    if param == "hardwareId" and value == cached_hardware_id:
        return value
    if param in {"treeName", "branch"} and tree_pair_cached:
        return value
    # treeId is a commit hash, and object ids are not kept.
    return pattern_segment


def _apply_pattern(pattern: str, path: str) -> str | None:
    # /$ is the not-found splat. It would accept every path.
    if pattern == "/$":
        return None
    pattern_segments = _segments(pattern)
    path_segments = _segments(path)
    if len(pattern_segments) != len(path_segments):
        return None
    values: dict[str, str] = {}
    for pattern_segment, path_segment in zip(
        pattern_segments, path_segments, strict=True
    ):
        if pattern_segment.startswith("$"):
            values[pattern_segment[1:]] = path_segment
        elif pattern_segment != path_segment:
            return None
    tree_name = values.get("treeName")
    branch = values.get("branch")
    tree_pair_cached = (
        tree_name is not None
        and branch is not None
        and _cached(_tree_cache, (tree_name, branch), _tree_pair_in_checkouts)
    )
    hardware_id = values.get("hardwareId")
    cached_hardware_id = (
        hardware_id
        if hardware_id is not None
        and _cached(_hardware_cache, hardware_id, _hardware_id_in_status)
        else None
    )
    label_segments = [
        _label_segment(pattern_segment, values, tree_pair_cached, cached_hardware_id)
        for pattern_segment in pattern_segments
    ]
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
    time_ms = serializers.IntegerField(min_value=0)


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
            min(body.validated_data["time_ms"] / 1000, MAX_VISIBLE_SECONDS)
        )
        return Response(status=HTTPStatus.NO_CONTENT)
