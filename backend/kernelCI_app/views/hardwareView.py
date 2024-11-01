import datetime
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from collections import defaultdict
from kernelCI_app.helpers.date import parseIntervalInDaysGetParameter
from kernelCI_app.helpers.errorHandling import ExceptionWithJsonResponse
from kernelCI_app.models import Tests
from kernelCI_app.helpers.build import build_status_map

DEFAULT_DAYS_INTERVAL = 3


class HardwareView(View):
    def __getSlowResult(self, start_date):
        tests = Tests.objects.filter(
            start_time__gte=start_date, environment_compatible__isnull=False
        ).values("environment_compatible", "status", "build__valid")

        hardware = {}
        for test in tests:
            for compatible in test["environment_compatible"]:
                if hardware.get(compatible) is None:
                    hardware[compatible] = {
                        "hardwareName": compatible,
                        "statusCount": defaultdict(int),
                        "buildCount": {"valid": 0, "invalid": 0, "null": 0},
                    }
                if test["status"] is None:
                    hardware[compatible]["statusCount"]["NULL"] += 1
                else:
                    hardware[compatible]["statusCount"][test["status"]] += 1

                build_status = build_status_map.get(test["build__valid"])
                if build_status is not None:
                    hardware[compatible]["buildCount"][build_status] += 1

        result = {"hardware": list(hardware.values())}

        return result

    def __getFastResult(self, start_date):
        hardwares = set()
        tests = Tests.objects.filter(
            start_time__gte=start_date, environment_compatible__isnull=False
        ).values("environment_compatible")

        for test in tests:
            for compatible in test["environment_compatible"]:
                hardwares.add(compatible)

        result = {"hardware": list(hardwares)}
        return result

    def get(self, request):
        mode = request.GET.get("mode", "fast")
        try:
            intervalInDays = parseIntervalInDaysGetParameter(
                request.GET.get("intervalInDays", DEFAULT_DAYS_INTERVAL)
            )
        except ExceptionWithJsonResponse as e:
            return e.getJsonResponse()

        start_date = timezone.now() - datetime.timedelta(days=intervalInDays)
        if mode == "fast":
            result = self.__getFastResult(start_date)
        elif mode == "slow":
            result = self.__getSlowResult(start_date)
        else:
            return JsonResponse({"error": "Invalid mode"}, status=400)

        return JsonResponse(result, safe=False)
