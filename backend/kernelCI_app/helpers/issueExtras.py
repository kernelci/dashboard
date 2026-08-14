from collections import defaultdict
from typing import List, Optional, Tuple

from kernelCI_app.constants.general import UNCATEGORIZED_STRING
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.queries.issues import (
    get_issue_first_seen_data,
    get_issue_last_seen_data,
    get_issue_next_checkout_data,
    get_issue_trees_data,
)
from kernelCI_app.typeModels.issues import (
    ExtraIssuesData,
    Incident,
    IssueWithExtraInfo,
    NextCheckout,
    ProcessedExtraDetailedIssues,
    TreeSetItem,
)


class TagUrls:
    MAINLINE_URL = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
    STABLE_URL = "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git"
    LINUX_NEXT_URL = (
        "https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git"
    )


def parse_issue(issue_str: Optional[str]) -> tuple[str, Optional[int]]:
    if issue_str is None:
        return (UNCATEGORIZED_STRING, None)
    issue_id, _, issue_version = issue_str.partition(",")
    issue_version = int(issue_version) if issue_version.upper() != "NULL" else None
    return (issue_id, issue_version)


def _incident_from_record(record: dict) -> Incident:
    return Incident(
        first_seen=record["first_seen"],
        git_commit_hash=record["git_commit_hash"],
        git_repository_url=record["git_repository_url"],
        git_repository_branch=record["git_repository_branch"],
        git_commit_name=record["git_commit_name"],
        tree_name=record["tree_name"],
        issue_version=record["issue_version"],
        checkout_id=record["checkout_id"],
    )


def _next_checkout_from_record(record: dict) -> NextCheckout:
    return NextCheckout(
        checkout_id=record["checkout_id"],
        start_time=record["start_time"],
        git_commit_hash=record["git_commit_hash"],
        git_commit_name=record["git_commit_name"],
        git_repository_url=record["git_repository_url"],
        git_repository_branch=record["git_repository_branch"],
        tree_name=record["tree_name"],
        origin=record["origin"],
    )


def process_issues_extra_details(
    *,
    issue_key_list: List[Tuple[str, int]],
    processed_issues_table: ProcessedExtraDetailedIssues,
) -> None:
    if len(issue_key_list) == 0:
        return

    # TODO: combine both queries into one
    assign_issue_incidents(
        issue_key_list=issue_key_list,
        processed_issues_table=processed_issues_table,
    )
    assign_issue_trees(
        issue_key_list=issue_key_list,
        processed_issues_table=processed_issues_table,
    )


def assign_issue_incidents(
    *,
    issue_key_list: List[Tuple[str, int]],
    processed_issues_table: ProcessedExtraDetailedIssues,
) -> None:
    """
    Assigns first/last seen and next-checkout data to the processed_issues_table
    by querying with the issue_key_list.
    """
    issue_id_set = {issue_id for issue_id, _ in issue_key_list}
    versions_per_issue: dict[str, set[int]] = defaultdict(set)

    for issue_id, issue_version in issue_key_list:
        versions_per_issue[issue_id].add(issue_version)

    issue_id_list = list(issue_id_set)
    first_incident_records = get_issue_first_seen_data(issue_id_list=issue_id_list)
    last_incident_records = get_issue_last_seen_data(issue_id_list=issue_id_list)
    next_checkout_records = get_issue_next_checkout_data(issue_id_list=issue_id_list)
    last_incident_by_id = {
        record["issue_id"]: record for record in last_incident_records
    }
    next_checkout_by_id = {
        record["issue_id"]: record for record in next_checkout_records
    }

    for record in first_incident_records:
        issue_id = record["issue_id"]
        last_record = last_incident_by_id.get(issue_id)
        next_record = next_checkout_by_id.get(issue_id)

        processed_issue_from_id = processed_issues_table.setdefault(
            issue_id,
            ExtraIssuesData(
                first_incident=_incident_from_record(record),
                last_incident=_incident_from_record(last_record),
                next_checkout=(
                    _next_checkout_from_record(next_record) if next_record else None
                ),
                versions={},
            ),
        )

        # Initialize the versions table with null because that version may or may not exist.
        # If an issue_version exists, the trees can be assigned with `assign_issue_trees`
        for version in versions_per_issue[issue_id]:
            processed_issue_from_id.versions.setdefault(version, None)


def assign_issue_trees(
    *,
    issue_key_list: list[tuple[str, int]],
    processed_issues_table: ProcessedExtraDetailedIssues,
) -> None:
    trees_records = get_issue_trees_data(issue_key_list=issue_key_list)

    for record in trees_records:
        issue_id = record["issue_id"]
        issue_version = record["issue_version"]
        git_repository_url = record["git_repository_url"]
        git_repository_branch = record["git_repository_branch"]
        tree_name = record["tree_name"]

        processed_issue_from_id = processed_issues_table.get(issue_id)
        if processed_issue_from_id is None:
            # While in `assign_issue_first_seen` we don't care about the difference
            # "issue exists" x "issue has no incident", here we do receive a row
            # even if an issue had no incidents (in order to make that difference)
            # In such case we can ignore the record since we won't return this data
            log_message(
                f"Got record for issue without incident {issue_id} {issue_version}"
            )
            continue

        issue_versions_map = processed_issue_from_id.versions

        current_detailed_issue = issue_versions_map.get(issue_version)
        if current_detailed_issue is None:
            issue_versions_map[issue_version] = IssueWithExtraInfo(
                id=issue_id, version=issue_version
            )
            current_detailed_issue = issue_versions_map[issue_version]

        if tree_name is not None and git_repository_branch is not None:
            current_detailed_issue.trees.append(
                TreeSetItem(
                    tree_name=record["tree_name"],
                    git_repository_branch=git_repository_branch,
                )
            )

        match (git_repository_url, git_repository_branch):
            case (TagUrls.MAINLINE_URL, "master"):
                current_detailed_issue.tags.add("mainline")
            case (TagUrls.STABLE_URL, branch) if branch is not None:
                current_detailed_issue.tags.add("stable")
            case (TagUrls.LINUX_NEXT_URL, "master" | "pending-fixes"):
                current_detailed_issue.tags.add("linux-next")
