from kernelCI_app.typeModels.issues import Issue, IssueDict
from kernelCI_app.utils import convert_issues_dict_to_list_typed, create_issue_typed


def sanitize_details_issues_rows(*, rows: list[dict]) -> list[Issue]:
    result: IssueDict = {}
    for row in rows:
        issue_id = row["id"]
        issue_version = row["version"]
        current_issue = result.get((issue_id, issue_version))
        if current_issue:
            current_issue.incidents_info.increment(row["status"])
        else:
            result[(issue_id, issue_version)] = create_issue_typed(
                issue_id=issue_id,
                issue_version=issue_version,
                issue_comment=row["comment"],
                issue_report_url=row["report_url"],
                starting_count_status=row["status"],
            )
    return convert_issues_dict_to_list_typed(issues_dict=result)
