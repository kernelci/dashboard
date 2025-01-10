from django.http import JsonResponse
from django.views import View
from kernelCI_app.helpers.filters import (
    should_increment_test_issue,
    UNKNOWN_STRING,
    FilterParams,
)
from kernelCI_app.helpers.treeDetails import call_based_on_compatible_and_misc_platform, decide_if_is_boot_filtered_out, decide_if_is_build_filtered_out, decide_if_is_full_row_filtered_out, decide_if_is_test_filtered_out, get_build, get_current_row_data, get_hardware_filter, get_tree_details_data, get_tree_url, is_test_boots_test, process_builds_issue, process_test_summary, process_tests_issue
from kernelCI_app.utils import (
    convert_issues_dict_to_list,
    create_issue,
    IncidentInfo,
)

from collections import defaultdict

from kernelCI_app.viewCommon import create_details_build_summary


class TreeDetails(View):
    def __init__(self):
        self.processedTests = set()
        self.filters = None

        self.testStatusSummary = {}
        self.testHistory = []
        self.test_configs = {}
        self.testPlatformsWithErrors = set()
        self.testFailReasons = {}
        self.test_arch_summary = {}
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


    def _process_boots_test(self, row_data):
        testId = row_data["test_id"]
        testStatus = row_data["test_status"]
        buildConfig = row_data["build_config_name"]
        buildArch = row_data["build_architecture"]
        buildCompiler = row_data["build_compiler"]
        testPlatform = row_data["test_platform"]
        testError = row_data["test_error"]
        historyItem = row_data["history_item"]
        incident_id = row_data["incident_id"]
        issue_id = row_data["issue_id"]
        issue_comment = row_data["issue_comment"]
        issue_report_url = row_data["issue_report_url"]
        testEnvironmentCompatible = row_data["test_environment_compatible"]
        incident_test_id = row_data["incident_test_id"]

        if decide_if_is_boot_filtered_out(self, row_data):
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

    def _process_non_boots_test(self, row_data):
        test_id = row_data["test_id"]
        history_item = row_data["history_item"]

        if decide_if_is_test_filtered_out(self, row_data):
            return

        process_tests_issue(self,row_data)

        if test_id in self.processedTests:
            return

        self.processedTests.add(test_id)
        self.testHistory.append(history_item)
        process_test_summary(self, row_data)

    def _process_builds(self, row_data):
        build_id = row_data["build_id"]

        if decide_if_is_build_filtered_out(self, row_data):
            return

        process_builds_issue(self, row_data)

        if build_id in self.processed_builds:
            return

        self.processed_builds.add(build_id)

        self.builds.append(get_build(row_data))

    def _sanitize_rows(self, rows):
        for row in rows:
            row_data = get_current_row_data(row)
            
            call_based_on_compatible_and_misc_platform(row_data, self.hardwareUsed.add)


            self.tree_url = get_tree_url(row_data, self.tree_url)

            is_record_filter_out = decide_if_is_full_row_filtered_out(self, row_data)

            if is_record_filter_out:
                continue

            if row_data["build_id"] is not None:
                self._process_builds(row_data)

            if is_test_boots_test(row_data):
                self._process_boots_test(row_data)
            else:
                self._process_non_boots_test(row_data)

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
                "testArchSummary": list(self.test_arch_summary.values()),
                "buildsSummary": self.build_summary,
                "bootFailReasons": self.bootFailReasons,
                "testFailReasons": self.testFailReasons,
                "testPlatformsWithErrors": list(self.testPlatformsWithErrors),
                "bootPlatformsFailing": list(self.bootPlatformsFailing),
                "testConfigs": self.test_configs,
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
