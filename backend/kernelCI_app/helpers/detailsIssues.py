from kernelCI_app.typeModels.issues import Issue, IssueDict
from kernelCI_app.utils import convert_issues_dict_to_list_typed, create_issue


def sanitize_details_issues_rows(*, rows) -> list[Issue]:
    result: IssueDict = {}
    for row in rows:
        issue_id = row["id"]
        issue_version = row["version"]
        current_issue = result.get((issue_id, issue_version))
        if current_issue:
            current_issue["incidents_info"]["incidentsCount"] += 1
        else:
            result[(issue_id, issue_version)] = create_issue(
                issue_id=issue_id,
                issue_version=issue_version,
                issue_comment=row["comment"],
                issue_report_url=row["report_url"],
            )
    return convert_issues_dict_to_list_typed(issues_dict=result)
