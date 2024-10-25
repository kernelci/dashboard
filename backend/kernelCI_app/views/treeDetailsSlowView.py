from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from kernelCI_app.utils import (
    FilterParams,
    convert_issues_dict_to_list,
    extract_error_message,
    extract_platform,
    InvalidComparisonOP,
    getErrorResponseBody,
    toIntOrDefault,
    create_issue,
    IncidentInfo,
)
from kernelCI_app.cache import getQueryCache, setQueryCache
from django.db import connection
from collections import defaultdict


class TreeDetailsSlow(View):
    def __init__(self):
        self.processedTests = set()
        self.filterTestDurationMin, self.filterTestDurationMax = None, None
        self.filterBootDurationMin, self.filterBootDurationMax = None, None
        self.filterBootStatus = set()
        self.filterTestStatus = set()
        self.filterTreeDetailsConfigs = set()
        self.filterTreeDetailsCompiler = set()
        self.filterArchitecture = set()
        self.filter_handlers = {
            "boot.status": self.__handle_boot_status,
            "boot.duration": self.__handle_boot_duration,
            "test.status": self.__handle_test_status,
            "test.duration": self.__handle_test_duration,
            "config_name": self.__handle_config_name,
            "compiler": self.__handle_compiler,
            "architecture": self.__handle_architecture,
        }

        self.testHistory = []
        self.testStatusSummary = {}
        self.testConfigs = {}
        self.testPlatformsWithErrors = set()
        self.testFailReasons = {}
        self.testArchSummary = {}
        self.testIssues = []
        self.testIssuesTable = {}
        self.testEnvironmentCompatible = defaultdict(lambda: defaultdict(int))
        self.bootHistory = []
        self.bootStatusSummary = {}
        self.bootConfigs = {}
        self.bootPlatformsFailing = set()
        self.bootFailReasons = {}
        self.bootArchSummary = {}
        self.bootIssues = []
        self.bootsIssuesTable = {}
        self.bootEnvironmentCompatible = defaultdict(lambda: defaultdict(int))
        self.incidentsIssueRelationship = defaultdict(
            lambda: IncidentInfo(incidentsCount=0)
        )
        self.hardwareUsed = set()

    def __handle_boot_status(self, current_filter):
        self.filterBootStatus.add(current_filter["value"])

    def __handle_boot_duration(self, current_filter):
        value = current_filter["value"]
        operation = current_filter["comparison_op"]
        if operation == "lte":
            self.filterBootDurationMax = toIntOrDefault(value, None)
        else:
            self.filterBootDurationMin = toIntOrDefault(value, None)

    def __handle_test_status(self, current_filter):
        self.filterTestStatus.add(current_filter["value"])

    def __handle_test_duration(self, current_filter):
        value = current_filter["value"]
        operation = current_filter["comparison_op"]
        if operation == "lte":
            self.filterTestDurationMax = toIntOrDefault(value, None)
        else:
            self.filterTestDurationMin = toIntOrDefault(value, None)

    def __handle_config_name(self, current_filter):
        self.filterTreeDetailsConfigs.add(current_filter["value"])

    def __handle_compiler(self, current_filter):
        self.filterTreeDetailsCompiler.add(current_filter["value"])

    def __handle_architecture(self, current_filter):
        self.filterArchitecture.add(current_filter["value"])

    def __processFilters(self, request):
        try:
            filter_params = FilterParams(request)
            for current_filter in filter_params.filters:
                field = current_filter["field"]
                # Delegate to the appropriate handler based on the field
                if field in self.filter_handlers:
                    self.filter_handlers[field](current_filter)
        except InvalidComparisonOP as e:
            return HttpResponseBadRequest(getErrorResponseBody(str(e)))

    def __getCurrentRowData(self, currentRow):
        tempColumnDict = {
            "tests_id": 1,
            "tests_origin": 2,
            "tests_environment_comment": 3,
            "tests_environment_misc": 4,
            "tests_path": 5,
            "tests_comment": 6,
            "tests_log_url": 7,
            "tests_status": 8,
            "tests_waived": 9,
            "tests_start_time": 10,
            "tests_duration": 11,
            "tests_number_value": 12,
            "tests_misc": 13,
            "tests_environment_compatible": 14,
            "builds_checkout_id": 15,
            "builds_id": 16,
            "builds_comment": 17,
            "builds_start_time": 18,
            "builds_duration": 19,
            "builds_architecture": 20,
            "builds_command": 21,
            "builds_compiler": 22,
            "builds_config_name": 23,
            "builds_config_url": 24,
            "builds_log_url": 25,
            "builds_valid": 26,
            "incident_id": 28,
            "incident_present": 29,
            "issue_id": 30,
            "issue_comment": 31,
            "issue_report_url": 32,
        }

        incident_id = currentRow[tempColumnDict["incident_id"]]
        incident_present = currentRow[tempColumnDict["incident_present"]]
        issue_id = currentRow[tempColumnDict["issue_id"]]
        issue_comment = currentRow[tempColumnDict["issue_comment"]]
        issue_report_url = currentRow[tempColumnDict["issue_report_url"]]
        path = currentRow[tempColumnDict["tests_path"]]
        testId = currentRow[tempColumnDict["tests_id"]]
        testStatus = currentRow[tempColumnDict["tests_status"]]
        if (testStatus is None):
            testStatus = "NULL"
        testDuration = currentRow[tempColumnDict["tests_duration"]]
        buildConfig = currentRow[tempColumnDict["builds_config_name"]]
        buildArch = currentRow[tempColumnDict["builds_architecture"]]
        buildCompiler = currentRow[tempColumnDict["builds_compiler"]]
        startTime = tempColumnDict["tests_start_time"]
        testPlatform = extract_platform(
            currentRow[tempColumnDict["tests_environment_misc"]]
        )
        testError = extract_error_message(currentRow[tempColumnDict["tests_misc"]])
        testEnvironmentCompatible = currentRow[
            tempColumnDict["tests_environment_compatible"]
        ]

        historyItem = {
            "id": testId,
            "status": testStatus,
            "path": path,
            "duration": testDuration,
            "startTime": currentRow[tempColumnDict["tests_start_time"]],
        }

        return (
            path,
            testId,
            testStatus,
            testDuration,
            buildConfig,
            buildArch,
            buildCompiler,
            testPlatform,
            testError,
            startTime,
            historyItem,
            incident_id,
            incident_present,
            issue_id,
            issue_comment,
            issue_report_url,
            testEnvironmentCompatible,
        )

    def __processBootsTest(self, currentRowData):
        (
            path,
            testId,
            testStatus,
            testDuration,
            buildConfig,
            buildArch,
            buildCompiler,
            testPlatform,
            testError,
            startTime,
            historyItem,
            incident_id,
            incident_present,
            issue_id,
            issue_comment,
            issue_report_url,
            testEnvironmentCompatible,
        ) = currentRowData

        if len(self.filterBootStatus) > 0 and (testStatus not in self.filterBootStatus):
            return
        if self.filterBootDurationMax is not None and (
            toIntOrDefault(testDuration, 0) > self.filterBootDurationMax
        ):
            return

        if self.filterBootDurationMin is not None and (
            toIntOrDefault(testDuration, 0) < self.filterBootDurationMin
        ):
            return

        if issue_id:
            currentIssue = self.bootsIssuesTable.get(issue_id)
            if currentIssue is None:
                currentIssue = create_issue(
                    issue_id=issue_id,
                    issue_comment=issue_comment,
                    issue_report_url=issue_report_url,
                )
                self.bootsIssuesTable[issue_id] = currentIssue
            currentIssue["incidents_info"]["incidentsCount"] += 1

        if testId in self.processedTests:
            return
        self.processedTests.add(testId)

        self.bootHistory.append(historyItem)
        self.bootStatusSummary[testStatus] = (
            self.bootStatusSummary.get(testStatus, 0) + 1
        )

        archKey = "%s-%s" % (buildArch, buildCompiler)
        archSummary = self.bootArchSummary.get(
            archKey,
            {"arch": buildArch, "compiler": buildCompiler, "status": {}},
        )
        archSummary["status"][testStatus] = archSummary["status"].get(testStatus, 0) + 1
        self.bootArchSummary[archKey] = archSummary

        configSummary = self.bootConfigs.get(buildConfig, {})
        configSummary[testStatus] = configSummary.get(testStatus, 0) + 1
        self.bootConfigs[buildConfig] = configSummary

        if testStatus == "ERROR" or testStatus == "FAIL" or testStatus == "MISS":
            self.bootPlatformsFailing.add(testPlatform)
            self.bootFailReasons[testError] = self.bootFailReasons.get(testError, 0) + 1

        if testEnvironmentCompatible is not None:
            self.bootEnvironmentCompatible[testEnvironmentCompatible][testStatus] += 1

            self.incidentsIssueRelationship[incident_id]["incidentsCount"] += 1

    def __processNonBootsTest(self, currentRowData):
        (
            path,
            testId,
            testStatus,
            testDuration,
            buildConfig,
            buildArch,
            buildCompiler,
            testPlatform,
            testError,
            startTime,
            historyItem,
            incident_id,
            incident_present,
            issue_id,
            issue_comment,
            issue_report_url,
            testEnvironmentCompatible,
        ) = currentRowData

        if len(self.filterTestStatus) > 0 and (testStatus not in self.filterTestStatus):
            return
        if self.filterTestDurationMax is not None and (
            toIntOrDefault(testDuration, 0) > self.filterTestDurationMax
        ):
            return
        if self.filterTestDurationMin is not None and (
            toIntOrDefault(testDuration, 0) < self.filterTestDurationMin
        ):
            return

        if issue_id:
            currentIssue = self.testIssuesTable.get(issue_id)
            if currentIssue is None:
                currentIssue = create_issue(
                    issue_id=issue_id,
                    issue_comment=issue_comment,
                    issue_report_url=issue_report_url,
                )
                self.testIssuesTable[issue_id] = currentIssue
            currentIssue["incidents_info"]["incidentsCount"] += 1
        if testId in self.processedTests:
            return
        self.processedTests.add(testId)

        self.testHistory.append(historyItem)
        self.testStatusSummary[testStatus] = (
            self.testStatusSummary.get(testStatus, 0) + 1
        )

        archKey = "%s-%s" % (buildArch, buildCompiler)
        archSummary = self.testArchSummary.get(
            archKey,
            {"arch": buildArch, "compiler": buildCompiler, "status": {}},
        )
        archSummary["status"][testStatus] = archSummary["status"].get(testStatus, 0) + 1
        self.testArchSummary[archKey] = archSummary

        configSummary = self.testConfigs.get(buildConfig, {})
        configSummary[testStatus] = configSummary.get(testStatus, 0) + 1
        self.testConfigs[buildConfig] = configSummary

        if testStatus == "ERROR" or testStatus == "FAIL" or testStatus == "MISS":
            self.testPlatformsWithErrors.add(testPlatform)
            self.testFailReasons[testError] = self.testFailReasons.get(testError, 0) + 1

        if testEnvironmentCompatible is not None:
            if testStatus is None:
                self.testEnvironmentCompatible[testEnvironmentCompatible]["NULL"] += 1
            else:
                self.testEnvironmentCompatible[testEnvironmentCompatible][testStatus] += 1

    def get(self, request, commit_hash: str | None):
        cache_key = "treeDetailsSlow"
        origin_param = request.GET.get("origin")
        git_url_param = request.GET.get("git_url")
        git_branch_param = request.GET.get("git_branch")
        self.__processFilters(request)

        params = {
            "commit_hash": commit_hash,
            "origin_param": origin_param,
            "git_url_param": git_url_param,
            "git_branch_param": git_branch_param,
        }

        rows = getQueryCache(cache_key, params)

        if rows is None:
            # Right now this query is only using for showing test data so it is doing inner joins
            # if it is needed for builds data they should become left join and the logic should be updated
            query = """
            SELECT
                    tests.build_id AS tests_build_id,
                    tests.id AS tests_id,
                    tests.origin AS tests_origin,
                    tests.environment_comment AS tests_environment_comment,
                    tests.environment_misc AS tests_environment_misc,
                    tests.path AS tests_path,
                    tests.comment AS tests_comment,
                    tests.log_url AS tests_log_url,
                    tests.status AS tests_status,
                    tests.waived AS tests_waived,
                    tests.start_time AS tests_start_time,
                    tests.duration AS tests_duration,
                    tests.number_value AS tests_number_value,
                    tests.misc AS tests_misc,
                    tests.environment_compatible[1] AS tests_environment_compatible,
                    builds_filter.*,
                    incidents.id,
                    incidents.present,
                    issues.id,
                    issues.comment,
                    issues.report_url
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
                    INNER JOIN builds
                        ON tree_head.checkout_id = builds.checkout_id
                    WHERE
                        builds.origin = %(origin_param)s
                ) AS builds_filter
            INNER JOIN tests
                ON builds_filter.builds_id = tests.build_id
            LEFT JOIN incidents
                ON tests.id = incidents.test_id
            LEFT JOIN issues
                ON incidents.issue_id = issues.id
            WHERE
                tests.origin = %(origin_param)s
            """
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                setQueryCache(cache_key, params, rows)

        for currentRow in rows:
            currentRowData = self.__getCurrentRowData(currentRow)

            (
                path,
                testId,
                testStatus,
                testDuration,
                buildConfig,
                buildArch,
                buildCompiler,
                testPlatform,
                testError,
                startTime,
                historyItem,
                incident_id,
                incident_present,
                issue_id,
                issue_comment,
                issue_report_url,
                testEnvironmentCompatible,
            ) = currentRowData

            if testEnvironmentCompatible is not None:
                self.hardwareUsed.add(testEnvironmentCompatible)

            if (
                (
                    len(self.filterArchitecture) > 0
                    and (buildArch not in self.filterArchitecture)
                )
                or (
                    len(self.filterTreeDetailsCompiler) > 0
                    and (buildCompiler not in self.filterTreeDetailsCompiler)
                )
                or (
                    len(self.filterTreeDetailsConfigs) > 0
                    and (buildConfig not in self.filterTreeDetailsConfigs)
                )
            ):
                continue

            if path.startswith("boot"):
                self.__processBootsTest(currentRowData)
            else:
                self.__processNonBootsTest(currentRowData)

        self.testIssues = convert_issues_dict_to_list(self.testIssuesTable)
        self.bootIssues = convert_issues_dict_to_list(self.bootsIssuesTable)

        return JsonResponse(
            {
                "bootArchSummary": list(self.bootArchSummary.values()),
                "testArchSummary": list(self.testArchSummary.values()),
                "bootFailReasons": self.bootFailReasons,
                "testFailReasons": self.testFailReasons,
                "testPlatformsWithErrors": list(self.testPlatformsWithErrors),
                "bootPlatformsFailing": list(self.bootPlatformsFailing),
                "testConfigs": self.testConfigs,
                "bootConfigs": self.bootConfigs,
                "testStatusSummary": self.testStatusSummary,
                "bootStatusSummary": self.bootStatusSummary,
                "bootHistory": self.bootHistory,
                "testHistory": self.testHistory,
                "bootIssues": self.bootIssues,
                "testIssues": self.testIssues,
                "testEnvironmentCompatible": self.testEnvironmentCompatible,
                "bootEnvironmentCompatible": self.bootEnvironmentCompatible,
                "incidentsIssueRelationship": self.incidentsIssueRelationship,
                "hardwareUsed": list(self.hardwareUsed),
            },
            safe=False,
        )
