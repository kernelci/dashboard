import http from "k6/http";
import { check } from "k6";

export default function () {
    const defaultRes = http.post(
        'http://test-backend:8000/api/hardware/kubernetes',
        JSON.stringify({
            "startTimestampInSeconds":1758378600,
            "endTimestampInSeconds":1758810600,
            "selectedCommits": {}
        }),
        {
            headers: {
                'Content-Type': 'application/json',
            },
        }
    );

    check(defaultRes, {
        'status is 200': (r) => r.status === 200,
        'response time < 500ms': (r) => r.timings.duration < 500,
    });
}
