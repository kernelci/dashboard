import http from "k6/http";
import { check } from "k6";

/*
* Retrieves the issue details for a random issue on the issue listing page.
*/
export default function () {
    const issueListingRes = http.get(
        "https://test-backend:8000/api/issue/\
        ?interval_in_days=5&filter_issue.culprit=code&filter_issue.options=hasIncident"
    );
    check(issueListingRes, {
        'issue listing status is 200': (r) => r.status === 200,
        'issue listing has body': (r) => r.body && r.body.length > 0,
    });

    const issueData = JSON.parse(issueListingRes.body);
    if (!issueData || issueData.length === 0 || issueData["issues"].length === 0) {
        console.log("No issues found, cannot proceed with details page test.");
        return;
    }

    const randomIndex = Math.floor(Math.random() * issueData["issues"].length);
    const selectedIssue = issueData["issues"][randomIndex];

    const issueId = selectedIssue.id;
    const issueVersion = selectedIssue.version;

    const issueDetailsRes = http.get(
        `https://test-backend:8000/api/issue/${issueId}/?version=${issueVersion}`
    );
    check(issueDetailsRes, {
        'issue details status is 200': (r) => r.status === 200,
        'issue details response time < 500ms': (r) => r.timings.duration < 500,
        'issue details has body': (r) => r.body && r.body.length > 0,
    });
}
