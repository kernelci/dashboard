from django.http import JsonResponse
from django.views import View
from kernelCI_app.helpers.filters import (
    FilterParams,
)
from kernelCI_app.helpers.treeDetails import call_based_on_compatible_and_misc_platform, decide_if_is_boot_filtered_out, decide_if_is_build_filtered_out, decide_if_is_full_row_filtered_out, decide_if_is_test_filtered_out, get_build, get_current_row_data, get_tree_details_data, get_tree_url, is_test_boots_test, process_builds_issue, process_test_summary, process_tests_issue
from kernelCI_app.typeModels.databases import Derivative
from kernelCI_app.utils import (
    convert_issues_dict_to_list,
)

from collections import defaultdict

from pydantic import BaseModel
from kernelCI_app.viewCommon import create_details_build_summary
from typing import List, Dict, Any

class Summary(BaseModel):
   bootArchSummary: List[Dict[str, Any]]
   testArchSummary: List[Dict[str, Any]]
   buildsSummary: Dict[str, Any]
   bootFailReasons: Dict[str, Any]
   testFailReasons: Dict[str, Any]
   testPlatformsWithErrors: List[str]
   bootPlatformsFailing: List[str]
   testConfigs: Dict[str, Any]
   bootConfigs: Dict[str, Any]
   testStatusSummary: Dict[str, Any]
   bootStatusSummary: Dict[str, Any]
   bootIssues: List[Dict[str, Any]]
   testIssues: List[Dict[str, Any]]
   testEnvironmentCompatible: Dict[str, Dict[str, int]]
   bootEnvironmentCompatible: Dict[str, Dict[str, int]]
   testEnvironmentMisc: Dict[str, Dict[str, int]]
   bootEnvironmentMisc: Dict[str, Dict[str, int]]
   hardwareUsed: List[str]
   failedTestsWithUnknownIssues: int
   failedBootsWithUnknownIssues: int
   buildsIssues: List[Dict[str, Any]]
   failedBuildsWithUnknownIssues: int
   treeUrl: str
class TreeDetailsSummary(View):
    def __init__(self):
        self.processedTests = set()
        self.filters = None

        self.testStatusSummary = {}
        self.test_configs = {}
        self.testPlatformsWithErrors = set()
        self.testFailReasons = {}
        self.test_arch_summary = {}
        self.testIssues = []
        self.testIssuesTable = {}
        self.testEnvironmentCompatible = defaultdict(lambda: defaultdict(int))
        self.testEnvironmentMisc = defaultdict(lambda: defaultdict(int))
        self.bootStatusSummary = {}
        self.bootConfigs = {}
        self.bootPlatformsFailing = set()
        self.bootFailReasons = {}
        self.bootArchSummary = {}
        self.bootIssues = []
        self.bootsIssuesTable = {}
        self.bootEnvironmentCompatible = defaultdict(lambda: defaultdict(int))
        self.bootEnvironmentMisc = defaultdict(lambda: defaultdict(int))
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
        test_id = row_data["test_id"]

        if decide_if_is_boot_filtered_out(self, row_data):
            return

        process_builds_issue(self, row_data)

        if test_id in self.processedTests:
            return
        self.processedTests.add(test_id)

    def _process_non_boots_test(self, row_data):
        test_id = row_data["test_id"]

        if decide_if_is_test_filtered_out(self, row_data):
            return

        process_tests_issue(self,row_data)

        if test_id in self.processedTests:
            return

        self.processedTests.add(test_id)
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

        print(Derivative(id="aaa").model_json_schema())
        return JsonResponse({})
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
                "bootIssues": self.bootIssues,
                "testIssues": self.testIssues,
                "testEnvironmentCompatible": self.testEnvironmentCompatible,
                "bootEnvironmentCompatible": self.bootEnvironmentCompatible,
                "testEnvironmentMisc": self.testEnvironmentMisc,
                "bootEnvironmentMisc": self.bootEnvironmentMisc,
                "hardwareUsed": list(self.hardwareUsed),
                "failedTestsWithUnknownIssues": self.failedTestsWithUnknownIssues,
                "failedBootsWithUnknownIssues": self.failedBootsWithUnknownIssues,
                "buildsIssues": self.build_issues,
                "failedBuildsWithUnknownIssues": self.failed_builds_with_unknown_issues,
                "treeUrl": self.tree_url,
            },
            safe=False,
        )
