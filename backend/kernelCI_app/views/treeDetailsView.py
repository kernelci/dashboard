from typing import List
from django.http import JsonResponse
from http import HTTPStatus
from django.views import View
from kernelCI_app.helpers.errorHandling import create_error_response
from kernelCI_app.helpers.filters import (
    FilterParams,
)
from kernelCI_app.helpers.treeDetails import (
    call_based_on_compatible_and_misc_platform,
    decide_if_is_boot_filtered_out,
    decide_if_is_build_filtered_out,
    decide_if_is_full_row_filtered_out,
    decide_if_is_test_filtered_out,
    get_build,
    get_current_row_data,
    get_tree_details_data,
    process_boots_issue,
    process_tree_url,
    is_test_boots_test,
    process_boots_summary,
    process_builds_issue,
    process_test_summary,
    process_tests_issue,
    process_filters,
)
from kernelCI_app.utils import (
    convert_issues_dict_to_list,
)

from collections import defaultdict

from kernelCI_app.viewCommon import create_details_build_summary

from kernelCI_app.typeModels.issues import Issue, IssueDict


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
        self.git_commit_tags = []

        self.global_configs = set()
        self.global_architectures = set()
        self.global_compilers = set()
        self.unfiltered_test_issues = set()
        self.unfiltered_boot_issues = set()
        self.unfiltered_build_issues = set()

    def _process_boots_test(self, row_data):
        test_id = row_data["test_id"]
        history_item = row_data["history_item"]

        if decide_if_is_boot_filtered_out(self, row_data):
            return

        process_boots_issue(self, row_data)

        if test_id in self.processedTests:
            return
        self.processedTests.add(test_id)
        self.bootHistory.append(history_item)
        process_boots_summary(self, row_data)

    def _process_non_boots_test(self, row_data):
        test_id = row_data["test_id"]
        history_item = row_data["history_item"]

        if decide_if_is_test_filtered_out(self, row_data):
            return

        process_tests_issue(self, row_data)

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
        first_iteration = True
        for row in rows:
            row_data = get_current_row_data(row)
            if first_iteration is True:
                self.git_commit_tags = row_data["checkout_git_commit_tags"]
                first_iteration = False

            call_based_on_compatible_and_misc_platform(row_data, self.hardwareUsed.add)

            process_tree_url(self, row_data)
            process_filters(self, row_data)

            is_record_filter_out = decide_if_is_full_row_filtered_out(self, row_data)

            if is_record_filter_out:
                continue

            if row_data["build_id"] is not None:
                self._process_builds(row_data)

            if row_data["test_id"] is None:
                continue

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

        if len(rows) == 0:
            return create_error_response(
                error_message="Tree not found", status_code=HTTPStatus.NOT_FOUND
            )

        self._sanitize_rows(rows)

        return JsonResponse(
            {
                "builds": self.builds,
                "boots": self.bootHistory,
                "tests": self.testHistory,
                "summary": {
                    "builds": {
                        "status": self.build_summary["builds"],
                        "architectures": self.build_summary["architectures"],
                        "configs": self.build_summary["configs"],
                        "issues": self.build_issues,
                        "unknown_issues": self.failed_builds_with_unknown_issues,
                    },
                    "boots": {
                        "status": self.bootStatusSummary,
                        "architectures": list(self.bootArchSummary.values()),
                        "configs": self.bootConfigs,
                        "issues": self.bootIssues,
                        "unknown_issues": self.failedBootsWithUnknownIssues,
                        "environment_compatible": self.bootEnvironmentCompatible,
                        "environment_misc": self.bootEnvironmentMisc,
                        "fail_reasons": self.bootFailReasons,
                        "failed_platforms": list(self.bootPlatformsFailing),
                    },
                    "tests": {
                        "status": self.testStatusSummary,
                        "architectures": list(self.test_arch_summary.values()),
                        "configs": self.test_configs,
                        "issues": self.testIssues,
                        "unknown_issues": self.failedTestsWithUnknownIssues,
                        "environment_compatible": self.testEnvironmentCompatible,
                        "environment_misc": self.testEnvironmentMisc,
                        "fail_reasons": self.testFailReasons,
                        "failed_platforms": list(self.testPlatformsWithErrors),
                    },
                },
                "common": {
                    "hardware": list(self.hardwareUsed),
                    "tree_url": self.tree_url,
                    "git_commit_tags": self.git_commit_tags,
                },
                "filters": {
                    "all": {
                        "configs": list(self.global_configs),
                        "architectures": list(self.global_architectures),
                        "compilers": list(self.global_compilers),
                    },
                    "builds": {
                        "issues": list(self.unfiltered_build_issues),
                    },
                    "boots": {
                        "issues": list(self.unfiltered_boot_issues),
                    },
                    "tests": {
                        "issues": list(self.unfiltered_test_issues),
                    },
                },
            },
            safe=False,
        )
