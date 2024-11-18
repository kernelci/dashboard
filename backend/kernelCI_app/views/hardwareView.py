from django.http import JsonResponse
from django.views import View
from collections import defaultdict
from kernelCI_app.helpers.date import parse_start_and_end_timestamps_in_seconds_to_datetime
from kernelCI_app.helpers.errorHandling import ExceptionWithJsonResponse
from kernelCI_app.models import Tests
from kernelCI_app.helpers.build import build_status_map
from kernelCI_app.constants.general import DEFAULT_ORIGIN


class HardwareView(View):
    def __getSlowResult(self, start_date, end_date, origin):
        tests = Tests.objects.filter(
            start_time__gte=start_date,
            start_time__lte=end_date,
            environment_compatible__isnull=False,
            origin=origin
        ).values("environment_compatible", "status", "build__valid", "path")

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

                build_status = build_status_map.get(test["build__valid"])
                if build_status is not None:
                    hardware[compatible]["buildCount"][build_status] += 1

        result = {"hardware": list(hardware.values())}

        return result

    def __getFastResult(self, start_date, end_date, origin):
        hardwares = set()
        tests = Tests.objects.filter(
            start_time__gte=start_date,
            start_time__lte=end_date,
            environment_compatible__isnull=False,
            origin=origin
        ).values("environment_compatible")

        for test in tests:
            for compatible in test["environment_compatible"]:
                hardwares.add(compatible)

        hardwareResult = []
        for hardware in hardwares:
            hardwareResult.append({"hardwareName": hardware})
        result = {"hardware": hardwareResult}
        return result

    def get(self, request):
        mode = request.GET.get("mode", "fast")
        origin = request.GET.get("origin", DEFAULT_ORIGIN)
        start_timestamp_str = request.GET.get("startTimestampInSeconds")
        end_timestamp_str = request.GET.get("endTimeStampInSeconds")

        try:
            (start_date, end_date) = parse_start_and_end_timestamps_in_seconds_to_datetime(
                start_timestamp_str, end_timestamp_str
            )
        except ExceptionWithJsonResponse as e:
            return e.getJsonResponse()

        if mode == "fast":
            result = self.__getFastResult(start_date, end_date, origin)
        elif mode == "slow":
            result = self.__getSlowResult(start_date, end_date, origin)
        else:
            return JsonResponse({"error": "Invalid mode"}, status=400)

        return JsonResponse(result, safe=False)
