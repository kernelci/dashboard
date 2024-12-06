from datetime import datetime
from django.db.models import Subquery
from django.http import JsonResponse
from django.views import View
from collections import defaultdict
from kernelCI_app.helpers.date import (
    parse_start_and_end_timestamps_in_seconds_to_datetime,
)
from kernelCI_app.helpers.errorHandling import ExceptionWithJsonResponse
from kernelCI_app.models import Tests
from kernelCI_app.helpers.build import build_status_map
from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.helpers.trees import get_tree_heads


class HardwareView(View):
    def _getResults(self, start_date: datetime, end_date: datetime, origin: str):
        processedBuilds = set()

        checkouts_subquery = get_tree_heads(
            origin, start_date, end_date
        )

        tests = Tests.objects.filter(
            environment_compatible__isnull=False,
            start_time__gte=start_date,
            start_time__lte=end_date,
            build__checkout__origin=origin,
            build__checkout__git_commit_hash__in=Subquery(checkouts_subquery),
        ).values(
            "environment_compatible", "status", "build__valid", "path", "build__id"
        )

        hardware = {}

        for test in tests:
            for compatible in test["environment_compatible"]:
                if hardware.get(compatible) is None:
                    hardware[compatible] = {
                        "hardwareName": compatible,
                        "testStatusCount": defaultdict(int),
                        "bootStatusCount": defaultdict(int),
                        "buildCount": {"valid": 0, "invalid": 0, "null": 0},
                    }
                statusCount = "testStatusCount"
                if test["path"].startswith("boot.") or test["path"] == "boot":
                    statusCount = "bootStatusCount"
                if test["status"] is None:
                    hardware[compatible][statusCount]["NULL"] += 1
                else:
                    hardware[compatible][statusCount][test["status"]] += 1

                buildKey = test["build__id"] + compatible
                if buildKey in processedBuilds:
                    continue
                processedBuilds.add(buildKey)

                build_status = build_status_map.get(test["build__valid"])

                if build_status is not None:
                    hardware[compatible]["buildCount"][build_status] += 1

        result = {"hardware": list(hardware.values())}

        return result

    def get(self, request):
        origin = request.GET.get("origin", DEFAULT_ORIGIN)
        start_timestamp_str = request.GET.get("startTimestampInSeconds")
        end_timestamp_str = request.GET.get("endTimeStampInSeconds")

        try:
            (start_date, end_date) = (
                parse_start_and_end_timestamps_in_seconds_to_datetime(
                    start_timestamp_str, end_timestamp_str
                )
            )
        except ExceptionWithJsonResponse as e:
            return e.getJsonResponse()

        result = self._getResults(start_date, end_date, origin)

        return JsonResponse(result, safe=False)
