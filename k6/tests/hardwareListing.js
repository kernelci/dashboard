import http from "k6/http";
import { check } from "k6";

export default function () {
    const defaultRes = http.get('http://test-backend:8000/api/hardware');
    check(defaultRes, {
        'status is 200': (r) => r.status === 200,
        'response time < 500ms': (r) => r.timings.duration < 500,
    });
}
