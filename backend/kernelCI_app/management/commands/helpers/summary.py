import os
from typing import Any, Literal, Optional

from django.conf import settings
from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.utils import read_yaml_file
from collections import defaultdict
from kernelCI_app.typeModels.issues import CheckoutIssue
from kernelCI_app.queries.notifications import (
    get_issues_summary_data,
)
from kernelCI_app.helpers.issueExtras import assign_issue_first_seen
from kernelCI_app.typeModels.issues import ProcessedExtraDetailedIssues

type PossibleReportOptions = Literal["ignore_default_recipients"]
"""The expected possible options in a report. If a new option is added, add it here too."""

type TreeKey = tuple[str, str, str]
"""A tuple (branch, giturl, origin)"""

type ReportConfigs = list[dict[str, Any]]
"""A list of dictionaries containing the definition/configuration of a report"""

SIGNUP_FOLDER = "notifications/subscriptions/"


def _assign_default_folders(*, base_dir: str, signup_folder: str) -> tuple[str, str]:
    base_dir_return = base_dir
    signup_folder_return = signup_folder

    if not base_dir:
        base_dir_return = settings.BACKEND_DATA_DIR
    if not signup_folder:
        signup_folder_return = SIGNUP_FOLDER

    return (base_dir_return, signup_folder_return)


def process_submissions_files(
    *,
    base_dir: Optional[str] = None,
    signup_folder: Optional[str] = None,
    summary_origins: Optional[list[str]] = None,
) -> tuple[set[TreeKey], dict[TreeKey, ReportConfigs]]:
    """Processes all submission files and returns the set of TreeKey and
    the dict linking each tree to its report props"""
    (base_dir, signup_folder) = _assign_default_folders(
        base_dir=base_dir, signup_folder=signup_folder
    )

    tree_key_set: set[TreeKey] = set()
    tree_prop_map: dict[TreeKey, ReportConfigs] = {}
    """Example:
    tree_prop_map[(master, <mainline_url>, maestro)] = [
        {
            branch: master
            always: true
        },
        {
            branch: master
            origin: microsoft
            options: {}
            recipients: []
        }
    ]
    """

    full_path = os.path.join(base_dir, signup_folder)
    for filename in os.listdir(full_path):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            file_path = os.path.join(signup_folder, filename)
            file_data = read_yaml_file(base_dir=base_dir, file=file_path)
            # Although there is a for loop here, there should only be a single tree per file
            for tree_name, tree_values in file_data.items():
                giturl = tree_values.get("url")
                default_recipients = tree_values.get("default_recipients")

                if tree_values.get("reports") is None:
                    continue

                for report in tree_values["reports"]:
                    branch = report["branch"]
                    origin = report.get("origin", DEFAULT_ORIGIN)
                    if summary_origins is not None and origin not in summary_origins:
                        continue

                    report["giturl"] = giturl
                    report["tree_name"] = tree_name
                    if default_recipients:
                        report["default_recipients"] = default_recipients

                    tree_key = (branch, giturl, origin)
                    tree_key_set.add(tree_key)
                    if tree_prop_map.get(tree_key) is None:
                        tree_prop_map[tree_key] = []
                    tree_prop_map[tree_key].append(report)
        else:
            log_message(
                f"Skipping file {filename} on loading summary files. Not a yaml file."
            )

    return tree_key_set, tree_prop_map


def get_build_issues_from_checkout(
    *, checkout_ids: list[str]
) -> tuple[dict[str, list[CheckoutIssue]], dict[str, list[str]]]:
    """
    Retrieve and process build issues for the specified checkouts.
    Returns a tuple where the first element contains build issues (including both new and pre-existing issues)
    and the second element contains builds that failed but have no related issues.
    """
    checkout_issue_record = get_issues_summary_data(checkout_ids=checkout_ids)

    issues_map: dict[str, list[dict]] = defaultdict(list)
    checkout_builds_without_issues: dict[str, list[str]] = defaultdict(list)
    issues_id_and_version_set: set[tuple[str, int]] = set()

    for issue in checkout_issue_record:
        issue_id = issue.get("issue_id")
        issue_version = issue.get("issue_version")
        checkout_id = issue.get("checkout_id")
        build_id = issue.get("build_id")

        if issue_id is None or issue_version is None:
            checkout_builds_without_issues[checkout_id].append(build_id)
            continue

        issues_map[issue_id].append(issue)
        issues_id_and_version_set.add((issue_id, issue_version))

    processed_issues_table: ProcessedExtraDetailedIssues = {}
    assign_issue_first_seen(
        issue_key_list=list(issues_id_and_version_set),
        processed_issues_table=processed_issues_table,
    )

    result_checkout_issues: dict[str, list[CheckoutIssue]] = defaultdict(list)

    for issue_id in processed_issues_table.keys():
        first_seen = processed_issues_table[issue_id].first_incident.first_seen
        issue_version = processed_issues_table[issue_id].first_incident.issue_version
        first_checkout_id = processed_issues_table[issue_id].first_incident.checkout_id

        processed_issues = issues_map[issue_id]

        for processed_issue in processed_issues:
            checkout_id = processed_issue.get("checkout_id")
            checkout_issue = CheckoutIssue(
                issue_id=processed_issue.get("issue_id"),
                build_id=processed_issue.get("build_id"),
                version=processed_issue.get("issue_version"),
                comment=processed_issue.get("comment", "No information"),
                culprit_code=processed_issue.get("culprit_code", False),
                culprit_tool=processed_issue.get("culprit_tool", False),
                culprit_harness=processed_issue.get("culprit_harness", False),
                report_url=processed_issue.get("report_url"),
                first_seen=first_seen,
                is_new_issue=first_checkout_id == checkout_id,
            )

            result_checkout_issues[checkout_issue.checkout_id].append(checkout_issue)

    return result_checkout_issues, checkout_builds_without_issues
