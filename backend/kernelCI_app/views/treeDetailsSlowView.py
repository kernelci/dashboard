import json
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

from kernelCI_app.viewCommon import create_details_build_summary


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
        self.filterHardware = set()
        self.filterTestPath = ""
        self.filterBootPath = ""
        self.filter_handlers = {
            "boot.status": self.__handle_boot_status,
            "boot.duration": self.__handle_boot_duration,
            "test.status": self.__handle_test_status,
            "test.duration": self.__handle_test_duration,
            "config_name": self.__handle_config_name,
            "compiler": self.__handle_compiler,
            "architecture": self.__handle_architecture,
            "test.hardware": self.__handle_hardware,
            "test.path": self.__handle_path,
            "boot.path": self.__handle_path,
            "valid": self._handle_build_valid,
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
        self.failedTestsWithUnknownIssues = 0
        self.failedBootsWithUnknownIssues = 0
        self.builds = []
        self.processed_builds = set()
        self.build_summary = {}
        self.issues = []
        self.failed_builds_with_unknown_issues = 0
        self.processed_issues_dict = {}
        self.tree_url = ""
        self.filterBuildValid = set()

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

    def __handle_hardware(self, current_filter):
        self.filterHardware.add(current_filter["value"])

    def __handle_path(self, current_filter):
        if current_filter["field"] == "boot.path":
            self.filterBootPath = current_filter["value"]
        else:
            self.filterTestPath = current_filter["value"]

    def _handle_build_valid(self, current_filter):
        self.filterBuildValid.add(current_filter["value"])

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
        tmp_test_env_comp_key = 14
        currentRowData = {
            "test_id": currentRow[1],
            "test_origin": currentRow[2],
            "test_environment_comment": currentRow[3],
            "test_environment_misc": currentRow[4],
            "test_path": currentRow[5],
            "test_comment": currentRow[6],
            "test_log_url": currentRow[7],
            "test_status": currentRow[8],
            "test_waived": currentRow[9],
            "test_start_time": currentRow[10],
            "test_duration": currentRow[11],
            "test_number_value": currentRow[12],
            "test_misc": currentRow[13],
            "test_environment_compatible": currentRow[tmp_test_env_comp_key],
            "build_id": currentRow[16],
            "build_comment": currentRow[17],
            "build_start_time": currentRow[18],
            "build_duration": currentRow[19],
            "build_architecture": currentRow[20],
            "build_command": currentRow[21],
            "build_compiler": currentRow[22],
            "build_config_name": currentRow[23],
            "build_config_url": currentRow[24],
            "build_log_url": currentRow[25],
            "build_valid": currentRow[26],
            "build_misc": currentRow[27],
            "checkout_id": currentRow[28],
            "checkout_git_repository_url": currentRow[29],
            "checkout_git_repository_branch": currentRow[30],
            "incident_id": currentRow[31],
            "incident_present": currentRow[32],
            "issue_id": currentRow[33],
            "issue_comment": currentRow[34],
            "issue_report_url": currentRow[35],
        }

        UNKNOWN_STRING = "Unknown"

        currentRowData["test_platform"] = extract_platform(currentRowData["test_environment_misc"])
        if (currentRowData["test_status"] is None):
            currentRowData["test_status"] = "NULL"
        currentRowData["test_error"] = extract_error_message(currentRowData["test_misc"])
        if (currentRowData["test_environment_compatible"] is None):
            currentRowData["test_environment_compatible"] = UNKNOWN_STRING
        else:
            currentRowData["test_environment_compatible"] = currentRowData["test_environment_compatible"][0]
        if (currentRowData["build_architecture"] is None):
            currentRowData["build_architecture"] = UNKNOWN_STRING
        if (currentRowData["build_compiler"] is None):
            currentRowData["build_compiler"] = UNKNOWN_STRING
        if (currentRowData["build_config_name"] is None):
            currentRowData["build_config_name"] = UNKNOWN_STRING
        if (currentRowData["build_misc"] is not None):
            currentRowData["build_misc"] = json.loads(currentRowData["build_misc"])

        currentRowData["history_item"] = {
            "id": currentRowData["test_id"],
            "status": currentRowData["test_status"],
            "path": currentRowData["test_path"],
            "duration": currentRowData["test_duration"],
            "startTime": currentRowData["test_start_time"],
            "hardware": currentRow[tmp_test_env_comp_key]
        }

        return currentRowData

    def __processBootsTest(self, currentRowData):
        testId = currentRowData["test_id"]
        testStatus = currentRowData["test_status"]
        testDuration = currentRowData["test_duration"]
        buildConfig = currentRowData["build_config_name"]
        buildArch = currentRowData["build_architecture"]
        buildCompiler = currentRowData["build_compiler"]
        testPlatform = currentRowData["test_platform"]
        testError = currentRowData["test_error"]
        historyItem = currentRowData["history_item"]
        incident_id = currentRowData["incident_id"]
        issue_id = currentRowData["issue_id"]
        issue_comment = currentRowData["issue_comment"]
        issue_report_url = currentRowData["issue_report_url"]
        testEnvironmentCompatible = currentRowData["test_environment_compatible"]
        testPath = currentRowData["test_path"]

        if (
            (
                self.filterBootPath != ""
                and (self.filterBootPath not in testPath)
            )
            or (
                len(self.filterBootStatus) > 0
                and (testStatus not in self.filterBootStatus)
            )
            or (
                (
                    self.filterBootDurationMax is not None
                    or self.filterBootDurationMin is not None
                )
                and testDuration is None
            )
            or (
                self.filterBootDurationMax is not None
                and (
                    toIntOrDefault(testDuration, 0) > self.filterBootDurationMax
                )
            )
            or (
                self.filterBootDurationMin is not None
                and (
                    toIntOrDefault(testDuration, 0) < self.filterBootDurationMin
                )
            )
        ):
            return

        if issue_id:
            currentIssue = self.bootsIssuesTable.get(issue_id)
            if currentIssue:
                currentIssue["incidents_info"]["incidentsCount"] += 1
            else:
                self.bootsIssuesTable[issue_id] = create_issue(
                    issue_id=issue_id,
                    issue_comment=issue_comment,
                    issue_report_url=issue_report_url,
                )
        elif testStatus == "FAIL":
            self.failedBootsWithUnknownIssues += 1

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

        self.bootEnvironmentCompatible[testEnvironmentCompatible][testStatus] += 1
        self.incidentsIssueRelationship[incident_id]["incidentsCount"] += 1

    def __nonBootsGuard(self, testStatus, testDuration, testPath):
        if self.filterTestPath != "" and self.filterTestPath not in testPath:
            return False
        if len(self.filterTestStatus) > 0 and (testStatus not in self.filterTestStatus):
            return False
        if (
            self.filterTestDurationMax is not None or self.filterTestDurationMin is not None
        ) and testDuration is None:
            return False
        if self.filterTestDurationMax is not None and (
            toIntOrDefault(testDuration, 0) > self.filterTestDurationMax
        ):
            return False
        if self.filterTestDurationMin is not None and (
            toIntOrDefault(testDuration, 0) < self.filterTestDurationMin
        ):
            return False
        return True

    def __processNonBootsTest(self, currentRowData):
        testId = currentRowData["test_id"]
        testStatus = currentRowData["test_status"]
        buildConfig = currentRowData["build_config_name"]
        buildArch = currentRowData["build_architecture"]
        buildCompiler = currentRowData["build_compiler"]
        testPlatform = currentRowData["test_platform"]
        testError = currentRowData["test_error"]
        historyItem = currentRowData["history_item"]
        issue_id = currentRowData["issue_id"]
        issue_comment = currentRowData["issue_comment"]
        issue_report_url = currentRowData["issue_report_url"]
        testEnvironmentCompatible = currentRowData["test_environment_compatible"]

        if not self.__nonBootsGuard(testStatus, currentRowData["test_duration"], currentRowData["test_path"]):
            return
        if issue_id:
            currentIssue = self.testIssuesTable.get(issue_id)
            if currentIssue:
                currentIssue["incidents_info"]["incidentsCount"] += 1
            else:
                self.testIssuesTable[issue_id] = create_issue(
                    issue_id=issue_id,
                    issue_comment=issue_comment,
                    issue_report_url=issue_report_url,
                )
        elif testStatus == "FAIL":
            self.failedTestsWithUnknownIssues += 1

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

        self.testEnvironmentCompatible[testEnvironmentCompatible][testStatus] += 1

    def _process_builds(self, row_data):
        build_id = row_data["build_id"]
        issue_id = row_data["issue_id"]
        build_valid = row_data["build_valid"]

        if len(self.filterBuildValid) > 0 and (str(build_valid).lower() not in self.filterBuildValid):
            return

        if issue_id:
            current_issue = self.processed_issues_dict.get(issue_id)
            if (current_issue):
                current_issue["incidents_info"]["incidentsCount"] += 1
            else:
                self.processed_issues_dict[issue_id] = _get_issue_details(row_data)
        elif build_id not in self.processed_builds and build_valid is False:
            self.failed_builds_with_unknown_issues += 1

        if build_id in self.processed_builds:
            return
        self.processed_builds.add(build_id)
        self.builds.append(_get_build(row_data))

    def _sanitize_rows(self, rows):
        for row in rows:
            row_data = self.__getCurrentRowData(row)

            test_path = row_data["test_path"]
            test_environment_compatible = row_data["test_environment_compatible"]
            git_repository_url = row_data["checkout_git_repository_url"]

            if (test_environment_compatible):
                self.hardwareUsed.add(test_environment_compatible)

            if (self.tree_url == "" and git_repository_url is not None):
                self.tree_url = git_repository_url

            if (
                (
                    len(self.filterHardware) > 0
                    and test_environment_compatible
                    and (test_environment_compatible not in self.filterHardware)
                )
                or (
                    len(self.filterArchitecture) > 0
                    and test_environment_compatible
                    and (row_data["build_architecture"] not in self.filterArchitecture)
                )
                or (
                    len(self.filterTreeDetailsCompiler) > 0
                    and (row_data["build_compiler"] not in self.filterTreeDetailsCompiler)
                )
                or (
                    len(self.filterTreeDetailsConfigs) > 0
                    and (row_data["build_config_name"] not in self.filterTreeDetailsConfigs)
                )
            ):
                continue

            self._process_builds(row_data)

            if test_path:
                if test_path.startswith("boot"):
                    self.__processBootsTest(row_data)
                else:
                    self.__processNonBootsTest(row_data)

        self.testIssues = convert_issues_dict_to_list(self.testIssuesTable)
        self.bootIssues = convert_issues_dict_to_list(self.bootsIssuesTable)
        self.build_summary = create_details_build_summary(self.builds)
        self.issues = convert_issues_dict_to_list(self.processed_issues_dict)

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
                    tests.environment_compatible AS tests_environment_compatible,
                    builds_filter.*,
                    incidents.id AS incidents_id,
                    incidents.present AS incidents_present,
                    issues.id AS issues_id,
                    issues.comment AS issues_comment,
                    issues.report_url AS issues_report_url
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
                        builds.misc AS builds_misc,
                        tree_head.*
                    FROM
                        (
                            SELECT
                                checkouts.id AS checkout_id,
                                checkouts.git_repository_url AS checkouts_git_repository_url,
                                checkouts.git_repository_branch AS checkouts_git_repository_branch
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
            LEFT JOIN tests
                ON builds_filter.builds_id = tests.build_id
            LEFT JOIN incidents
                ON tests.id = incidents.test_id OR
                   builds_filter.builds_id = incidents.build_id
            LEFT JOIN issues
                ON incidents.issue_id = issues.id
            WHERE
                tests.origin = %(origin_param)s OR
                tests.origin IS NULL
            """
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                setQueryCache(cache_key, params, rows)

        self._sanitize_rows(rows)

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
                "failedTestsWithUnknownIssues": self.failedTestsWithUnknownIssues,
                "failedBootsWithUnknownIssues": self.failedBootsWithUnknownIssues,
                "builds": self.builds,
                "buildsSummary": self.build_summary,
                "buildsIssues": self.issues,
                "failedBuildsWithUnknownIssues": self.failed_builds_with_unknown_issues,
                "treeUrl": self.tree_url,
            },
            safe=False,
        )


def _get_build(row_data):
    return {
        "id": row_data["build_id"],
        "architecture": row_data["build_architecture"],
        "config_name": row_data["build_config_name"],
        "misc": row_data["build_misc"],
        "config_url": row_data["build_config_url"],
        "compiler": row_data["build_compiler"],
        "valid": row_data["build_valid"],
        "duration": row_data["build_duration"],
        "log_url": row_data["build_log_url"],
        "start_time": row_data["build_start_time"],
        "git_repository_url": row_data["checkout_git_repository_url"],
        "git_repository_branch": row_data["checkout_git_repository_branch"],
    }


def _get_issue_details(row_data):
    return create_issue(
        issue_id=row_data["issue_id"],
        issue_comment=row_data["issue_comment"],
        issue_report_url=row_data["issue_report_url"],
    )
