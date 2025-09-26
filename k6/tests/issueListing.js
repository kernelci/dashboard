import http from "k6/http";
import { check } from "k6";

export default function () {
    // The default frontend page already has some filters
    const defaultRes = http.get('http://test-backend:8000/api/issue/\
        ?filter_issue.culprit=code&filter_issue.options=hasIncident');
    check(defaultRes, {
        'filtered listing status is 200': (r) => r.status === 200,
        'filtered listing response time < 500ms': (r) => r.timings.duration < 500,
    });

    const cleanRes = http.get('http://test-backend:8000/api/issue/');
    check(cleanRes, {
        'clean listing status is 200': (r) => r.status === 200,
        'clean listing response time < 500ms': (r) => r.timings.duration < 500,
    });
}
