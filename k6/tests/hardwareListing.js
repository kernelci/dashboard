import http from "k6/http";
import { check } from "k6";

export const options = {
    iterations: 100,
};

// TODO: have a dev-friendly time and convert it before sending the request
export default function () {
    const defaultRes = http.get('http://test-backend:8000/api/hardware?startTimestampInSeconds=1760643000&endTimestampInSeconds=1761075000&origin=maestro');
    check(defaultRes, {
        'status is 200': (r) => r.status === 200,
        'response time < 500ms': (r) => r.timings.duration < 500,
    });
}
