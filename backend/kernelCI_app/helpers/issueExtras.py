from collections import defaultdict
from typing import Dict, List, Set, Tuple

from kernelCI_app.helpers.logger import log_message
from kernelCI_app.typeModels.issues import (
    IssueWithExtraInfo,
    ProcessedExtraDetailedIssues,
    TreeSetItem,
    FirstIncident,
)
from kernelCI_app.models import Incidents, Checkouts


class TagUrls:
    MAINLINE_URL = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
    STABLE_URL = "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git"
    LINUX_NEXT_URL = (
        "https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git"
    )


def process_issues_extra_details(
    *,
    issue_key_list: List[Tuple[str, int]],
    processed_issues_table: ProcessedExtraDetailedIssues,
) -> None:
    # TODO: combine both queries into one
    assign_issue_first_seen(
        issue_key_list=issue_key_list,
        processed_issues_table=processed_issues_table,
    )
    assign_issue_trees(
        issue_key_list=issue_key_list,
        processed_issues_table=processed_issues_table,
    )


def assign_issue_first_seen(
    *,
    issue_key_list: List[Tuple[str, int]],
    processed_issues_table: ProcessedExtraDetailedIssues,
) -> None:
    issue_id_list: List[str] = []
    versions_per_issue: Dict[str, Set[int]] = defaultdict(set)
    for issue_key in issue_key_list:
        issue_id, issue_version = issue_key
        issue_id_list.append(issue_id)
        versions_per_issue[issue_id].add(issue_version)

    # TODO: use '=' instead of 'IN' when the list has a single element
    incident_records = Incidents.objects.raw(
        """
        WITH first_incident AS (
            SELECT
                IC.issue_id,
                MIN(IC.issue_version) AS min_issue_version,
                MIN(IC._timestamp) AS first_seen
            FROM
                incidents IC
            WHERE
                IC.issue_id IN ({0})
            GROUP BY
                IC.issue_id
        )
        SELECT
            IC.id,
            IC.issue_id,
            IC._timestamp AS first_seen,
            IC.issue_version,
            C.git_commit_hash,
            C.git_repository_url,
            C.git_repository_branch
        FROM
            incidents IC
        LEFT JOIN tests T ON IC.test_id = T.id
        LEFT JOIN builds B ON (IC.build_id = B.id OR T.build_id = B.id)
        LEFT JOIN checkouts C ON B.checkout_id = C.id
        JOIN first_incident FI ON (
            IC.issue_id = FI.issue_id
            AND IC.issue_version = FI.min_issue_version
            AND IC."_timestamp" = FI.first_seen
        )
        """.format(", ".join(["%s"] * len(issue_id_list))),
        issue_id_list,
    )

    for record in incident_records:
        record_issue_id = record.issue_id
        first_seen = record.first_seen
        first_git_commit_hash = record.git_commit_hash
        first_git_repository_url = record.git_repository_url
        first_git_repository_branch = record.git_repository_branch

        processed_issue_from_id = processed_issues_table.get(record_issue_id)
        if processed_issue_from_id is None:
            processed_issues_table[record_issue_id] = {}
            processed_issue_from_id = processed_issues_table[record_issue_id]
            processed_issue_from_id["first_incident"] = FirstIncident(
                first_seen=first_seen,
                git_commit_hash=first_git_commit_hash,
                git_repository_url=first_git_repository_url,
                git_repository_branch=first_git_repository_branch,
            )

        for version in versions_per_issue[record_issue_id]:
            processed_issue_from_version = processed_issue_from_id.get(version)
            processed_issue_from_id["versions"] = {}
            if processed_issue_from_version is None:
                processed_issue_from_id["versions"][version] = IssueWithExtraInfo(
                    id=record_issue_id, version=version, first_seen=first_seen
                )


def assign_issue_trees(
    *,
    issue_key_list: List[Tuple[str, int]],
    processed_issues_table: ProcessedExtraDetailedIssues,
) -> None:
    # TODO: use '=' instead of 'IN' when the list has a single element
    tuple_param_list = []
    params = {}

    for index, key in enumerate(issue_key_list):
        id_key = f"id{index}"
        version_key = f"version{index}"

        tuple_string = f"(%({id_key})s, %({version_key})s)"

        tuple_param_list.append(tuple_string)
        params[id_key] = key[0]
        params[version_key] = key[1]
    tuple_str = ", ".join(tuple_param_list)

    trees_records = Checkouts.objects.raw(
        f"""
        SELECT DISTINCT
          ON (
            C.TREE_NAME,
            C.GIT_REPOSITORY_URL,
            C.GIT_REPOSITORY_BRANCH,
            IC.ISSUE_ID,
            IC.ISSUE_VERSION
          )
          C.ID,
          C.TREE_NAME,
          C.GIT_REPOSITORY_URL,
          C.GIT_REPOSITORY_BRANCH,
          IC.ISSUE_ID,
          IC.ISSUE_VERSION
        FROM
          INCIDENTS IC
          LEFT JOIN TESTS T ON IC.TEST_ID = T.ID
          LEFT JOIN BUILDS B ON (
            IC.BUILD_ID = B.ID
            OR T.BUILD_ID = B.ID
          )
          JOIN CHECKOUTS C ON B.CHECKOUT_ID = C.ID
        WHERE
          (IC.ISSUE_ID, IC.ISSUE_VERSION) IN ({tuple_str})
        """,
        params,
    )

    for record in trees_records:
        issue_id = record.issue_id
        issue_version = record.issue_version
        git_repository_url = record.git_repository_url
        git_repository_branch = record.git_repository_branch

        processed_issue_from_id = processed_issues_table.get(issue_id)
        if processed_issue_from_id is None:
            log_message("Got tree for issue id that is not on the list")
            continue

        current_detailed_issue = processed_issue_from_id["versions"].get(issue_version)
        if current_detailed_issue is None:
            log_message("Got tree for issue version that is not on the list")
            continue

        current_detailed_issue.trees.append(
            TreeSetItem(
                tree_name=record.tree_name,
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
