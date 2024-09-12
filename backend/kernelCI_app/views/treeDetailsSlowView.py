from django.http import JsonResponse
from django.views import View
from kernelCI_app.utils import extract_error_message, extract_platform
from django.db import connection


class TreeDetailsSlow(View):
    def get(self, request, commit_hash: str | None):
        origin_param = request.GET.get("origin")
        git_url_param = request.GET.get("git_url")
        git_branch_param = request.GET.get("git_branch")
        query = """
        SELECT
                tests.build_id AS tests_build_id,
                tests.id AS tests_id,
                tests.origin AS tests_origin,
                tests.environment_comment AS tests_enviroment_comment,
                tests.environment_misc AS tests_enviroment_misc,
                tests.path AS tests_path,
                tests.comment AS tests_comment,
                tests.log_url AS tests_log_url,
                tests.status AS tests_status,
                tests.waived AS tests_waived,
                tests.start_time AS tests_start_time,
                tests.duration AS tests_duration,
                tests.number_value AS tests_number_value,
                tests.misc AS tests_misc,
                builds_filter.*
        FROM
            (
                SELECT
                    builds.checkout_id AS builds_checkout_id,
                    builds.id AS builds_id,
                    builds.comment AS builds_comment,
                    builds.start_time AS builds_start_time,
                    builds.duration AS builds_duration,
                    builds.architecture AS builds_architecture,
                    builds.command AS builds_command,
                    builds.compiler AS builds_compiler,
                    builds.config_name AS builds_config_name,
                    builds.config_url AS builds_config_url,
                    builds.log_url AS builds_log_url,
                    builds.valid AS builds_valid,
                    tree_head.*
                FROM
                    (
                        SELECT
                            checkouts.id AS checkout_id
                        FROM
                            checkouts
                        WHERE
                            checkouts.git_commit_hash = %(commit_hash)s AND
                            checkouts.git_repository_url = %(git_url_param)s AND
                            checkouts.git_repository_branch = %(git_branch_param)s AND
                            checkouts.origin = %(origin_param)s
                    ) AS tree_head
                LEFT JOIN builds
                    ON tree_head.checkout_id = builds.checkout_id
                WHERE
                    builds.origin = %(origin_param)s
            ) AS builds_filter
        LEFT JOIN tests
            ON builds_filter.builds_id = tests.build_id
        WHERE
            tests.origin = %(origin_param)s
        """
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                {
                    "commit_hash": commit_hash,
                    "origin_param": origin_param,
                    "git_url_param": git_url_param,
                    "git_branch_param": git_branch_param,
                },
            )
            rows = cursor.fetchall()

        testHistory = []
        testStatusSummary = {}
        testConfigs = {}
        testPlatformsWithErrors = set()
        testFailReasons = {}
        testArchSummary = {}
        bootHistory = []
        bootStatusSummary = {}
        bootConfigs = {}
        bootPlatformsFailing = set()
        bootFailReasons = {}
        bootArchSummary = {}

        tempColumnDict = {
            "tests_id": 1,
            "tests_origin": 2,
            "tests_enviroment_comment": 3,
            "tests_enviroment_misc": 4,
            "tests_path": 5,
            "tests_comment": 6,
            "tests_log_url": 7,
            "tests_status": 8,
            "tests_waived": 9,
            "tests_start_time": 10,
            "tests_duration": 11,
            "tests_number_value": 12,
            "tests_misc": 13,
            "builds_checkout_id": 14,
            "builds_id": 15,
            "builds_comment": 16,
            "builds_start_time": 17,
            "builds_duration": 18,
            "builds_architecture": 19,
            "builds_command": 20,
            "builds_compiler": 21,
            "builds_config_name": 22,
            "builds_config_url": 23,
            "builds_log_url": 24,
            "builds_valid": 25,
        }
        t = tempColumnDict
        for r in rows:
            path = r[t["tests_path"]]
            testId = r[t["tests_id"]]
            testStatus = r[t["tests_status"]]
            buildConfig = r[t["builds_config_name"]]
            buildArch = r[t["builds_architecture"]]
            buildCompiler = r[t["builds_compiler"]]

            testPlatform = extract_platform(r[t["tests_misc"]])
            testError = extract_error_message(r[t["tests_misc"]])

            #  Test history for boot and non boot
            historyItem = {
                "id": testId,
                "status": testStatus,
                "path": path,
                "duration": r[t["tests_duration"]],
                "startTime": r[t["tests_start_time"]],
            }
            if path.startswith("boot"):
                bootHistory.append(historyItem)
                bootStatusSummary[testStatus] = bootStatusSummary.get(
                    testStatus, 0) + 1

                archKey = "%s-%s" % (buildArch, buildCompiler)
                archSummary = bootArchSummary.get(archKey, {
                    "arch": buildArch,
                    "compiler": buildCompiler,
                    "status": {}
                })
                archSummary["status"][testStatus] = archSummary["status"].get(testStatus, 0) + 1
                bootArchSummary[archKey] = archSummary

                configSummary = bootConfigs.get(buildConfig, {})
                configSummary[testStatus] = configSummary.get(
                    testStatus, 0) + 1
                bootConfigs[buildConfig] = configSummary

                if testStatus == "ERROR" or testStatus == "FAIL" or testStatus == "MISS":
                    bootPlatformsFailing.add(testPlatform)
                    bootFailReasons[testError] = bootFailReasons.get(
                        testError, 0) + 1
            else:
                testHistory.append(historyItem)
                testStatusSummary[testStatus] = testStatusSummary.get(
                    testStatus, 0) + 1

                archKey = "%s-%s" % (buildArch, buildCompiler)
                archSummary = testArchSummary.get(archKey, {
                    "arch": buildArch,
                    "compiler": buildCompiler,
                    "status": {}
                })
                archSummary["status"][testStatus] = archSummary["status"].get(testStatus, 0) + 1
                testArchSummary[archKey] = archSummary

                configSummary = testConfigs.get(buildConfig, {})
                configSummary[testStatus] = configSummary.get(
                    testStatus, 0) + 1
                testConfigs[buildConfig] = configSummary

                if testStatus == "ERROR" or testStatus == "FAIL" or testStatus == "MISS":
                    testPlatformsWithErrors.add(testPlatform)
                    testFailReasons[testError] = testFailReasons.get(
                        testError, 0) + 1

        return JsonResponse(
            {
                "bootArchSummary": list(bootArchSummary.values()),
                "testArchSummary": list(testArchSummary.values()),
                "bootFailReasons": bootFailReasons,
                "testFailReasons": testFailReasons,
                "testPlatformsWithErrors": list(testPlatformsWithErrors),
                "bootPlatformsFailing": list(bootPlatformsFailing),
                "testConfigs": testConfigs,
                "bootConfigs": bootConfigs,
                "testStatusSummary": testStatusSummary,
                "bootStatusSummary": bootStatusSummary,
                "bootHistory": bootHistory,
                "testHistory": testHistory
            },
            safe=False
        )
