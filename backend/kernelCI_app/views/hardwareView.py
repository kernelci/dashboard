from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Set
from django.db import models
from django.db.models import Subquery
from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from kernelCI_app.helpers.build import build_status_map
from kernelCI_app.helpers.errorHandling import (
    create_api_error_response,
)
from kernelCI_app.constants.general import UNKNOWN_STRING, MAESTRO_DUMMY_BUILD_PREFIX
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.helpers.misc import env_misc_value_or_default, handle_environment_misc
from kernelCI_app.helpers.trees import get_tree_heads
from kernelCI_app.models import Tests
from kernelCI_app.typeModels.hardwareListing import (
    HardwareItem,
    HardwareQueryParams,
    HardwareQueryParamsDocumentationOnly,
    HardwareResponse,
)
from kernelCI_app.utils import is_boot


class HardwareView(APIView):
    def _make_hardware_item(self, *, compatible: str, platform: str) -> HardwareItem:
        return {
            "hardware_name": compatible,
            "platform": platform,
            "test_status_summary": defaultdict(int),
            "boot_status_summary": defaultdict(int),
            "build_status_summary": {"valid": 0, "invalid": 0, "null": 0},
        }

    def _get_tests_from_database(
        self, start_date: datetime, end_date: datetime, origin: str
    ):
        checkouts_subquery = get_tree_heads(origin, start_date, end_date)

        return Tests.objects.filter(
            models.Q(environment_compatible__isnull=False)
            | models.Q(environment_misc__platform__isnull=False),
            start_time__gte=start_date,
            start_time__lte=end_date,
            build__checkout__origin=origin,
            build__checkout__git_commit_hash__in=Subquery(checkouts_subquery),
        ).values(
            "environment_compatible",
            "environment_misc",
            "status",
            "build__valid",
            "path",
            "build__id",
            "id",
        )

    def _handle_hardware_with_multiple_platforms(
        self, *, platform: str, current_hardware_name: str
    ):
        current_hardware = self.hardware[current_hardware_name]

        if current_hardware is None:
            return

        # Platform is a possible updater, if it is unknown there is nothing to update.
        if platform is UNKNOWN_STRING:
            return

        if current_hardware["platform"] is UNKNOWN_STRING:
            current_hardware["platform"] = platform
            return

        if current_hardware["platform"] == platform:
            return

        if isinstance(current_hardware["platform"], str):
            current_platform = current_hardware["platform"]
            current_hardware["platform"] = {current_platform}

        current_hardware["platform"].add(platform)

    def _process_hardware(
        self, *, test, current_hardware: str, current_platform: str
    ) -> None:
        test_key = test["id"] + current_hardware
        if test_key in self.processed_tests:
            return

        self.processed_tests.add(test_key)

        if self.hardware.get(current_hardware) is None:
            self.hardware[current_hardware] = self._make_hardware_item(
                compatible=current_hardware, platform=current_platform
            )

        self._handle_hardware_with_multiple_platforms(
            platform=current_platform, current_hardware_name=current_hardware
        )

        status_count = "test_status_summary"

        if is_boot(test["path"]):
            status_count = "boot_status_summary"

        test_status = "NULL" if test["status"] is None else test["status"]
        self.hardware[current_hardware][status_count][test_status] += 1

        build_key = test["build__id"] + current_hardware
        if build_key in self.processed_builds or test["build__id"].startswith(
            MAESTRO_DUMMY_BUILD_PREFIX
        ):
            return

        self.processed_builds.add(build_key)

        build_status = build_status_map.get(test["build__valid"])

        if build_status is not None:
            self.hardware[current_hardware]["build_status_summary"][build_status] += 1
        else:
            log_message(
                f"Hardware Listing -> Unknown Build status: {test["build__valid"]}"
            )

    def _get_results(
        self, start_date: datetime, end_date: datetime, origin: str
    ) -> HardwareResponse:
        self.processed_builds: Set[str] = set()
        self.processed_tests: Set[str] = set()
        self.hardware: Dict[str, HardwareItem] = {}

        tests = self._get_tests_from_database(start_date, end_date, origin)

        for test in tests:
            environment_misc = env_misc_value_or_default(
                handle_environment_misc(test["environment_misc"])
            )
            platform = environment_misc["platform"]
            environment_compatible = test["environment_compatible"]

            if environment_compatible is None and platform is UNKNOWN_STRING:
                continue

            if environment_compatible is None:
                self._process_hardware(
                    test=test, current_hardware=platform, current_platform=platform
                )
                continue

            for compatible in environment_compatible:
                self._process_hardware(
                    test=test, current_hardware=compatible, current_platform=platform
                )

        other_result: List[HardwareItem] = list(self.hardware.values())

        result: HardwareResponse = HardwareResponse(hardware=other_result)

        return result

    @extend_schema(
        parameters=[HardwareQueryParamsDocumentationOnly], responses=HardwareResponse
    )
    def get(self, request: Request):
        try:
            query_params = HardwareQueryParams(
                start_date=request.GET.get("startTimestampInSeconds"),
                end_date=request.GET.get("endTimeStampInSeconds"),
                origin=request.GET.get("origin"),
            )

            start_date: datetime = query_params.start_date
            end_date: datetime = query_params.end_date
            origin = query_params.origin
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        try:
            result = self._get_results(start_date, end_date, origin)

            if len(result.hardware) < 1:
                return create_api_error_response(
                    error_message="No hardwares found", status_code=HTTPStatus.OK
                )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(data=result.model_dump(), status=HTTPStatus.OK)
