from datetime import datetime
import math

from django.db import connection

from kernelCI_app.constants.general import MAESTRO_DUMMY_BUILD_PREFIX
from kernelCI_app.constants.ingester import INGEST_BATCH_SIZE
from kernelCI_app.models import (
    BuildStatusByHardware,
    Builds,
    NewBuild,
    NewTest,
    Tests,
)
from kernelCI_app.utils import is_boot


def ceil_to_next_half_hour(dt_input: str) -> int:
    half_hour_in_seconds = 1800
    timestamp = datetime.fromisoformat(dt_input).timestamp()
    return math.ceil(timestamp / half_hour_in_seconds) * half_hour_in_seconds


def convert_test(t: Tests) -> NewTest:
    is_boot_test = is_boot(t.path)
    start_time = ceil_to_next_half_hour(t.start_time)
    return NewTest(
        test_id=t.id,
        build_id=t.build_id,
        test_origin=t.origin,
        test_platform=t.environment_misc.get("platform"),
        test_compatible=t.environment_compatible,
        status=t.status,
        is_boot=is_boot_test,
        start_time=start_time,
    )


def convert_to_build_status_by_hardware(test: NewTest) -> BuildStatusByHardware:
    return BuildStatusByHardware(
        hardware_origin=test.test_origin,
        hardware_platform=test.test_platform,
        build_id=test.build_id,
    )


def prepare_build_status_by_hardware(
    tests: list[NewTest],
) -> list[BuildStatusByHardware]:
    return [convert_to_build_status_by_hardware(test) for test in tests]


def aggregate_hardware_status_data(tests: list[NewTest]) -> dict:
    aggregated_data = {}

    for test in tests:
        pass_count = 1 if test.status == "PASS" else 0
        failed_count = 1 if test.status == "FAIL" else 0
        inc_count = 1 if test.status not in ("PASS", "FAIL") else 0

        key = (test.test_origin, test.test_platform, test.start_time)

        if key not in aggregated_data:
            aggregated_data[key] = {
                "hardware_origin": test.test_origin,
                "hardware_platform": test.test_platform,
                "date": test.start_time,
                "compatibles": test.test_compatible,
                "build_pass": 0,
                "build_failed": 0,
                "build_inc": 0,
                "boot_pass": 0,
                "boot_failed": 0,
                "boot_inc": 0,
                "test_pass": 0,
                "test_failed": 0,
                "test_inc": 0,
            }

        if aggregated_data[key]["compatibles"] is None and test.test_compatible:
            aggregated_data[key]["compatibles"] = test.test_compatible

        if test.is_boot:
            aggregated_data[key]["boot_pass"] += pass_count
            aggregated_data[key]["boot_failed"] += failed_count
            aggregated_data[key]["boot_inc"] += inc_count
        else:
            aggregated_data[key]["test_pass"] += pass_count
            aggregated_data[key]["test_failed"] += failed_count
            aggregated_data[key]["test_inc"] += inc_count

    return aggregated_data


def convert_build(b: Builds) -> NewBuild:
    return NewBuild(
        build_id=b.id,
        checkout_id=b.checkout_id,
        build_origin=b.origin,
        status=b.status,
    )


def aggregate_builds_status(builds_instances: list[Builds]) -> None:
    builds_filtered = (
        b for b in builds_instances if not b.id.startswith(MAESTRO_DUMMY_BUILD_PREFIX)
    )

    builds_to_insert = (convert_build(b) for b in builds_filtered)

    NewBuild.objects.bulk_create(
        builds_to_insert,
        batch_size=INGEST_BATCH_SIZE,
        ignore_conflicts=True,
    )


def aggregate_tests_status(tests_instances: list[Tests]) -> None:
    tests_filtered = (
        t
        for t in tests_instances
        if t.environment_misc and t.environment_misc.get("platform")
    )
    tests_to_insert = (convert_test(t) for t in tests_filtered)

    with connection.cursor() as cursor:
        tests_created = NewTest.objects.bulk_create(
            tests_to_insert,
            batch_size=INGEST_BATCH_SIZE,
            ignore_conflicts=True,
        )

        build_status_by_hardware = prepare_build_status_by_hardware(tests_created)
        BuildStatusByHardware.objects.bulk_create(
            build_status_by_hardware,
            batch_size=INGEST_BATCH_SIZE,
            ignore_conflicts=True,
        )

        aggregated_data = aggregate_hardware_status_data(tests_created)

        if aggregated_data:
            insert_query = """
                INSERT INTO hardware_status (
                    hardware_origin, hardware_platform, date, compatibles,
                    build_pass, build_failed, build_inc,
                    boot_pass, boot_failed, boot_inc,
                    test_pass, test_failed, test_inc
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (hardware_origin, hardware_platform, date)
                DO UPDATE SET
                    compatibles = COALESCE(hardware_status.compatibles, EXCLUDED.compatibles),
                    boot_pass = hardware_status.boot_pass + EXCLUDED.boot_pass,
                    boot_failed = hardware_status.boot_failed + EXCLUDED.boot_failed,
                    boot_inc = hardware_status.boot_inc + EXCLUDED.boot_inc,
                    test_pass = hardware_status.test_pass + EXCLUDED.test_pass,
                    test_failed = hardware_status.test_failed + EXCLUDED.test_failed,
                    test_inc = hardware_status.test_inc + EXCLUDED.test_inc
            """

            values = [
                (
                    data["hardware_origin"],
                    data["hardware_platform"],
                    data["date"],
                    data["compatibles"],
                    data["build_pass"],
                    data["build_failed"],
                    data["build_inc"],
                    data["boot_pass"],
                    data["boot_failed"],
                    data["boot_inc"],
                    data["test_pass"],
                    data["test_failed"],
                    data["test_inc"],
                )
                for data in aggregated_data.values()
            ]

            cursor.executemany(insert_query, values)
