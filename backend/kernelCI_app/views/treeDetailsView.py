from typing import Dict, List, Tuple
from django.http import JsonResponse
from django.views import View
from kernelCI_app.helpers.filters import (
    should_increment_test_issue,
    UNKNOWN_STRING,
    FilterParams,
)
from kernelCI_app.utils import (
    Issue,
    convert_issues_dict_to_list,
    extract_error_message,
    create_issue,
    IncidentInfo,
)
from kernelCI_app.helpers.misc import (
    handle_build_misc,
    handle_environment_misc,
    build_misc_value_or_default,
    env_misc_value_or_default
)
from kernelCI_app.cache import getQueryCache, setQueryCache
from django.db import connection
from collections import defaultdict

from kernelCI_app.viewCommon import create_details_build_summary

type IssueDict = Dict[Tuple[str, str], Issue]


class TreeDetails(View):
    def __init__(self):
        self.processedTests = set()
        self.filterParams = None

        self.testHistory = []
        self.testStatusSummary = {}
        self.testConfigs = {}
        self.testPlatformsWithErrors = set()
        self.testFailReasons = {}
        self.testArchSummary = {}
        self.testIssues: List[Issue] = []
        self.testIssuesTable: IssueDict = {}
        self.testEnvironmentCompatible = defaultdict(lambda: defaultdict(int))
        self.testEnvironmentMisc = defaultdict(lambda: defaultdict(int))
        self.bootHistory = []
        self.bootStatusSummary = {}
        self.bootConfigs = {}
        self.bootPlatformsFailing = set()
        self.bootFailReasons = {}
        self.bootArchSummary = {}
        self.bootIssues: List[Issue] = []
        self.bootsIssuesTable: IssueDict = {}
        self.bootEnvironmentCompatible = defaultdict(lambda: defaultdict(int))
        self.bootEnvironmentMisc = defaultdict(lambda: defaultdict(int))
        self.incidentsIssueRelationship = defaultdict(
            lambda: IncidentInfo(incidentsCount=0)
        )
        self.hardwareUsed = set()
        self.failedTestsWithUnknownIssues = 0
        self.failedBootsWithUnknownIssues = 0
        self.builds = []
        self.processed_builds = set()
        self.build_summary = {}
        self.build_issues: List[Issue] = []
        self.failed_builds_with_unknown_issues = 0
        self.processed_build_issues: IssueDict = {}
        self.tree_url = ""

    def setup_filters(self):
        self.filterTestDurationMin = self.filterParams.filterTestDurationMin
        self.filterTestDurationMax = self.filterParams.filterTestDurationMax
        self.filterBootDurationMin = self.filterParams.filterBootDurationMin
        self.filterBootDurationMax = self.filterParams.filterBootDurationMax
        self.filterBootStatus = self.filterParams.filterBootStatus
        self.filterTestStatus = self.filterParams.filterTestStatus
        self.filterTreeDetailsConfigs = self.filterParams.filterConfigs
        self.filterTreeDetailsCompiler = self.filterParams.filterCompiler
        self.filterArchitecture = self.filterParams.filterArchitecture
        self.filterHardware = self.filterParams.filterHardware
        self.filterTestPath = self.filterParams.filterTestPath
        self.filterBootPath = self.filterParams.filterBootPath
        self.filterBuildValid = self.filterParams.filterBuildValid
        self.filterIssues = self.filterParams.filterIssues

    def _getCurrentRowData(self, currentRow):
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
            "incident_test_id": currentRow[32],
            "incident_present": currentRow[33],
            "issue_id": currentRow[34],
            "issue_version": currentRow[35],
            "issue_comment": currentRow[36],
            "issue_report_url": currentRow[37],
        }

        environment_misc = handle_environment_misc(
            currentRowData["test_environment_misc"]
        )
        currentRowData["test_platform"] = env_misc_value_or_default(
            environment_misc
        ).get("platform")
        if currentRowData["test_status"] is None:
            currentRowData["test_status"] = "NULL"
        currentRowData["test_error"] = extract_error_message(
            currentRowData["test_misc"]
        )
        if currentRowData["test_environment_compatible"] is None:
            currentRowData["test_environment_compatible"] = UNKNOWN_STRING
        else:
            currentRowData["test_environment_compatible"] = currentRowData[
                "test_environment_compatible"
            ][0]
        if currentRowData["build_architecture"] is None:
            currentRowData["build_architecture"] = UNKNOWN_STRING
        if currentRowData["build_compiler"] is None:
            currentRowData["build_compiler"] = UNKNOWN_STRING
        if currentRowData["build_config_name"] is None:
            currentRowData["build_config_name"] = UNKNOWN_STRING
        if currentRowData["issue_id"] is None and (
            currentRowData["build_valid"] is False
            or currentRowData["build_valid"] is None
            or currentRowData["test_status"] == "FAIL"
        ):
            currentRowData["issue_id"] = UNKNOWN_STRING
        currentRowData["build_misc"] = handle_build_misc(currentRowData["build_misc"])

        currentRowData["history_item"] = {
            "id": currentRowData["test_id"],
            "status": currentRowData["test_status"],
            "path": currentRowData["test_path"],
            "duration": currentRowData["test_duration"],
            "startTime": currentRowData["test_start_time"],
            "hardware": currentRow[tmp_test_env_comp_key],
        }

        return currentRowData

    def _processBootsTest(self, currentRowData):
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
        issue_version = currentRowData["issue_version"]
        issue_comment = currentRowData["issue_comment"]
        issue_report_url = currentRowData["issue_report_url"]
        testEnvironmentCompatible = currentRowData["test_environment_compatible"]
        testPath = currentRowData["test_path"]
        incident_test_id = currentRowData["incident_test_id"]

        is_boot_filter_out = self.filterParams.is_boot_filtered_out(
            duration=testDuration,
            issue_id=issue_id,
            path=testPath,
            status=testStatus,
            incident_test_id=incident_test_id,
        )

        if is_boot_filter_out:
            return

        can_insert_issue = should_increment_test_issue(
            issue_id=issue_id, incident_test_id=incident_test_id
        )

        if issue_id and can_insert_issue:
            currentIssue = self.bootsIssuesTable.get((issue_id, issue_version))
            if currentIssue:
                currentIssue["incidents_info"]["incidentsCount"] += 1
            else:
                self.bootsIssuesTable[(issue_id, issue_version)] = create_issue(
                    issue_id=issue_id,
                    issue_version=issue_version,
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

        if testEnvironmentCompatible != UNKNOWN_STRING:
            self.bootEnvironmentCompatible[testEnvironmentCompatible][testStatus] += 1
        else:
            self.bootEnvironmentMisc[testPlatform][testStatus] += 1

        self.incidentsIssueRelationship[incident_id]["incidentsCount"] += 1

    def __processNonBootsTest(self, currentRowData):
        testId = currentRowData["test_id"]
        testStatus = currentRowData["test_status"]
        testDuration = currentRowData["test_duration"]
        buildConfig = currentRowData["build_config_name"]
        buildArch = currentRowData["build_architecture"]
        buildCompiler = currentRowData["build_compiler"]
        testPlatform = currentRowData["test_platform"]
        testError = currentRowData["test_error"]
        historyItem = currentRowData["history_item"]
        issue_id = currentRowData["issue_id"]
        issue_version = currentRowData["issue_version"]
        issue_comment = currentRowData["issue_comment"]
        issue_report_url = currentRowData["issue_report_url"]
        testEnvironmentCompatible = currentRowData["test_environment_compatible"]
        testPath = currentRowData["test_path"]
        incident_test_id = currentRowData["incident_test_id"]

        is_test_filter_out = self.filterParams.is_test_filtered_out(
            duration=testDuration,
            issue_id=issue_id,
            path=testPath,
            status=testStatus,
            incident_test_id=incident_test_id,
        )

        if is_test_filter_out:
            return

        can_insert_issue = should_increment_test_issue(issue_id, incident_test_id)

        if issue_id and can_insert_issue:
            currentIssue = self.testIssuesTable.get((issue_id, issue_version))
            if currentIssue:
                currentIssue["incidents_info"]["incidentsCount"] += 1
            else:
                self.testIssuesTable[(issue_id, issue_version)] = create_issue(
                    issue_id=issue_id,
                    issue_version=issue_version,
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

        if testEnvironmentCompatible != UNKNOWN_STRING:
            self.testEnvironmentCompatible[testEnvironmentCompatible][testStatus] += 1
        else:
            self.testEnvironmentMisc[testPlatform][testStatus] += 1

    def _process_builds(self, row_data):
        build_id = row_data["build_id"]
        issue_id = row_data["issue_id"]
        issue_version = row_data["issue_version"]
        build_valid = row_data["build_valid"]
        build_duration = row_data["build_duration"]

        is_build_filtered_out = self.filterParams.is_build_filtered_out(
            valid=build_valid, duration=build_duration, issue_id=issue_id
        )

        if is_build_filtered_out:
            return

        if issue_id and (build_valid is False or build_valid is None):
            current_issue = self.processed_build_issues.get((issue_id, issue_version))
            if current_issue:
                current_issue["incidents_info"]["incidentsCount"] += 1
            else:
                self.processed_build_issues[(issue_id, issue_version)] = create_issue(
                    issue_id=issue_id,
                    issue_version=issue_version,
                    issue_comment=row_data["issue_comment"],
                    issue_report_url=row_data["issue_report_url"],
                )
        elif build_id not in self.processed_builds and build_valid is False:
            self.failed_builds_with_unknown_issues += 1

        if build_id in self.processed_builds:
            return
        self.processed_builds.add(build_id)
        self.builds.append(_get_build(row_data))

    def _sanitize_rows(self, rows):
        for row in rows:
            row_data = self._getCurrentRowData(row)

            test_path = row_data["test_path"]
            test_environment_compatible = row_data["test_environment_compatible"]
            test_environment_misc_platform = row_data["test_platform"]
            build_misc_platform = build_misc_value_or_default(
                row_data["build_misc"]
            ).get("platform", UNKNOWN_STRING)
            hardware_filter = test_environment_compatible
            git_repository_url = row_data["checkout_git_repository_url"]

            if test_environment_compatible != UNKNOWN_STRING:
                self.hardwareUsed.add(test_environment_compatible)
            elif test_environment_misc_platform != UNKNOWN_STRING:
                hardware_filter = test_environment_misc_platform
                self.hardwareUsed.add(test_environment_misc_platform)
            else:
                hardware_filter = build_misc_platform
                self.hardwareUsed.add(build_misc_platform)

            if self.tree_url == "" and git_repository_url is not None:
                self.tree_url = git_repository_url

            record_filter_out = self.filterParams.is_record_filtered_out(
                hardwares=[hardware_filter],
                architecture=row_data["build_architecture"],
                compiler=row_data["build_compiler"],
                config_name=row_data["build_config_name"],
            )

            if record_filter_out:
                continue

            if row_data["build_id"] is not None:
                self._process_builds(row_data)

            if test_path:
                if test_path.startswith("boot"):
                    self._processBootsTest(row_data)
                else:
                    self.__processNonBootsTest(row_data)

        self.testIssues = convert_issues_dict_to_list(self.testIssuesTable)
        self.bootIssues = convert_issues_dict_to_list(self.bootsIssuesTable)
        self.build_summary = create_details_build_summary(self.builds)
        self.build_issues = convert_issues_dict_to_list(self.processed_build_issues)

    def get(self, request, commit_hash: str | None):
        cache_key = "treeDetailsSlow"
        origin_param = request.GET.get("origin")
        git_url_param = request.GET.get("git_url")
        git_branch_param = request.GET.get("git_branch")
        self.filterParams = FilterParams(request)
        self.setup_filters()

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
                    incidents.test_id AS incidents_test_id,
                    incidents.present AS incidents_present,
                    issues.id AS issues_id,
                    issues.version AS issues_version,
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
                "testEnvironmentMisc": self.testEnvironmentMisc,
                "bootEnvironmentMisc": self.bootEnvironmentMisc,
                "incidentsIssueRelationship": self.incidentsIssueRelationship,
                "hardwareUsed": list(self.hardwareUsed),
                "failedTestsWithUnknownIssues": self.failedTestsWithUnknownIssues,
                "failedBootsWithUnknownIssues": self.failedBootsWithUnknownIssues,
                "builds": self.builds,
                "buildsSummary": self.build_summary,
                "buildsIssues": self.build_issues,
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
