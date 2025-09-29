def create_issue_dict(
    issue_id="issue1",
    version=1,
    comment="Test comment",
    report_url="http://example.com",
    status="PASS",
):
    return {
        "id": issue_id,
        "version": version,
        "comment": comment,
        "report_url": report_url,
        "status": status,
    }


issue1_dict = create_issue_dict()
issue2_dict = create_issue_dict(
    issue_id="issue2",
    version=2,
    comment="Test comment 2",
    report_url="http://example.com/2",
    status="FAIL",
)
