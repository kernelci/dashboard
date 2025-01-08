from django.http import JsonResponse
from django.views import View
from kernelCI_app.helpers.filters import (
    should_increment_test_issue,
    UNKNOWN_STRING,
    FilterParams,
)
from kernelCI_app.helpers.treeDetails import get_current_row_data, get_tree_details_data
from kernelCI_app.utils import (
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

from collections import defaultdict

from kernelCI_app.viewCommon import create_details_build_summary


class TreeDetails(View):
    def __init__(self):
        self.processedTests = set()
        self.filters = None

        self.testStatusSummary = {}
        self.testHistory = []
        self.testConfigs = {}
        self.testPlatformsWithErrors = set()
        self.testFailReasons = {}
        self.testArchSummary = {}
        self.testIssues = []
        self.testIssuesTable = {}
        self.testEnvironmentCompatible = defaultdict(lambda: defaultdict(int))
        self.testEnvironmentMisc = defaultdict(lambda: defaultdict(int))
        self.bootHistory = []
        self.bootStatusSummary = {}
        self.bootConfigs = {}
        self.bootPlatformsFailing = set()
        self.bootFailReasons = {}
        self.bootArchSummary = {}
        self.bootIssues = []
        self.bootsIssuesTable = {}
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
        self.build_issues = []
        self.failed_builds_with_unknown_issues = 0
        self.processed_build_issues = {}
        self.tree_url = ""


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
        incident_test_id = currentRowData["incident_test_id"]

        is_boot_filter_out = self.filters.is_boot_filtered_out(
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
        issue_comment = currentRowData["issue_comment"]
        issue_report_url = currentRowData["issue_report_url"]
        testEnvironmentCompatible = currentRowData["test_environment_compatible"]
        testPath = currentRowData["test_path"]
        incident_test_id = currentRowData["incident_test_id"]

        is_test_filter_out = self.filters.is_test_filtered_out(
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

        if testEnvironmentCompatible != UNKNOWN_STRING:
            self.testEnvironmentCompatible[testEnvironmentCompatible][testStatus] += 1
        else:
            self.testEnvironmentMisc[testPlatform][testStatus] += 1

    def _process_builds(self, row_data):
        build_id = row_data["build_id"]
        issue_id = row_data["issue_id"]
        build_valid = row_data["build_valid"]
        build_duration = row_data["build_duration"]

        is_build_filtered_out = self.filters.is_build_filtered_out(
            valid=build_valid, duration=build_duration, issue_id=issue_id
        )

        if is_build_filtered_out:
            return

        if issue_id and (build_valid is False or build_valid is None):
            current_issue = self.processed_build_issues.get(issue_id)
            if current_issue:
                current_issue["incidents_info"]["incidentsCount"] += 1
            else:
                self.processed_build_issues[issue_id] = create_issue(
                    issue_id=row_data["issue_id"],
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
            row_data = get_current_row_data(row)

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

            record_filter_out = self.filters.is_record_filtered_out(
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
                    self.__processBootsTest(row_data)
                else:
                    self.__processNonBootsTest(row_data)

        self.testIssues = convert_issues_dict_to_list(self.testIssuesTable)
        self.bootIssues = convert_issues_dict_to_list(self.bootsIssuesTable)
        self.build_summary = create_details_build_summary(self.builds)
        self.build_issues = convert_issues_dict_to_list(self.processed_build_issues)

    def get(self, request, commit_hash: str | None):
        rows = get_tree_details_data(request, commit_hash)

        self.filters = FilterParams(request)

        self._sanitize_rows(rows)

        return JsonResponse(
            {
                "bootArchSummary": list(self.bootArchSummary.values()),
                "testArchSummary": list(self.testArchSummary.values()),
                "buildsSummary": self.build_summary,
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
